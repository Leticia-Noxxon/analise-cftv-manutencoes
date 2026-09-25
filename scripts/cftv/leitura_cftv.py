"""F5 — Leitura e consolidação dos 'Relatório CFTV' (somente leitura de data/raw).

Regras (REGRAS_PROJETO.md §2–§4):
- localizar todos os .xlsx cujo nome começa com 'Relatório CFTV';
- listar todas as abas; ignorar abas com tabela dinâmica / sem cabeçalho de registros;
- usar a aba com cabeçalho 'Prefixo' + colunas 'Câmera NN'; se 0 ou >1 abas se qualificarem -> ERRO (não adivinhar);
- padronizar cabeçalhos (NFC, trim, espaços múltiplos) e Empresa (trim); preservar valores originais;
- guardar arquivo_origem e linha_excel.
"""
import datetime as dt
import re
import unicodedata
from pathlib import Path

import openpyxl
import pandas as pd

from . import config
from .interpretacao import interpretar_camera, status_geral, vazio


class ErroEstrutura(Exception):
    pass


def nfc(s):
    return unicodedata.normalize('NFC', s) if isinstance(s, str) else s


def norm_header(h):
    if h is None:
        return None
    return re.sub(r'\s+', ' ', nfc(str(h))).strip()


def data_do_nome(path: Path):
    m = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', path.name)
    return dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1))) if m else None


def listar_arquivos_cftv(raw: Path = config.RAW):
    fs = [p for p in raw.glob('*.xlsx') if nfc(p.name).startswith('Relatório CFTV') and not p.name.startswith('~$')]
    return sorted(fs, key=lambda p: (data_do_nome(p) or dt.date.max, p.name))


def classificar_aba(ws):
    pivots = len(getattr(ws, '_pivots', []) or [])
    primeira = next(ws.iter_rows(min_row=1, max_row=1, values_only=True), ())
    hdr = [norm_header(h) for h in primeira]
    tem_prefixo = 'Prefixo' in hdr
    tem_cam = any(h and re.match(r'^C[âa]mera \d+$', h) for h in hdr)
    if pivots:
        return False, f'ignorada: contém {pivots} tabela(s) dinâmica(s) (resumo), não é base de registros'
    if tem_prefixo and tem_cam:
        return True, 'utilizada: cabeçalho Prefixo + Câmera NN na linha 1 (registros reais)'
    return False, 'ignorada: sem cabeçalho de registros (Prefixo + Câmera NN)'


def ler_arquivo(path: Path):
    wb = openpyxl.load_workbook(path, data_only=True)  # somente leitura: nunca salvar
    info = {'arquivo': path.name, 'data_arquivo': data_do_nome(path), 'abas': [], 'aba_utilizada': None,
            'abas_ignoradas': []}
    candidatas = []
    for ws in wb.worksheets:
        ok, motivo = classificar_aba(ws)
        info['abas'].append(ws.title)
        (candidatas.append(ws) if ok else info['abas_ignoradas'].append({'aba': ws.title, 'motivo': motivo}))
    if len(candidatas) != 1:
        raise ErroEstrutura(f'{path.name}: {len(candidatas)} abas de registros encontradas — revisar manualmente')
    ws = candidatas[0]
    info['aba_utilizada'] = ws.title
    linhas = list(ws.iter_rows(values_only=True))
    cab_orig = list(linhas[0])
    cab = [norm_header(h) for h in cab_orig]
    info['colunas_originais'] = [c for c in cab_orig if c is not None]
    registros = []
    for i, r in enumerate(linhas[1:], start=2):
        if all(vazio(v) for v in r):
            continue
        d = {c: v for c, v in zip(cab, r) if c}
        d['linha_excel'] = i
        registros.append(d)
    info['registros'] = len(registros)
    info['linhas_vazias_desconsideradas'] = len(linhas) - 1 - len(registros)
    return registros, info


def _fmt_manut(v):
    if vazio(v):
        return None
    if isinstance(v, (dt.datetime, dt.date)):
        return v.strftime('%Y-%m-%d')
    return str(v).strip()


def consolidar(raw: Path = config.RAW):
    """Retorna (DataFrame consolidado 1 linha por prefixo×data, lista de infos por arquivo)."""
    todos, infos = [], []
    for p in listar_arquivos_cftv(raw):
        regs, info = ler_arquivo(p)
        infos.append(info)
        datas_col = set()
        for d in regs:
            data = d.get('Data')
            data = data.date() if isinstance(data, dt.datetime) else data
            datas_col.add(data)
            row = {
                'prefixo': int(d['Prefixo']),
                'data': data,
                'empresa': str(d.get('Empresa') or '').strip(),
                'empresa_original': d.get('Empresa'),
                'status_operacional_cftv': (str(d['Status']).strip() if not vazio(d.get('Status')) else None),
                'ultima_manutencao_cftv': _fmt_manut(d.get('Manutenção')) if 'Manutenção' in d else None,
                'coluna_manutencao_presente': 'Manutenção' in d,
                'ultima_transmissao': (str(d['Última Transmissão']) if not vazio(d.get('Última Transmissão')) else None),
                'arquivo_origem': info['arquivo'],
                'aba_origem': info['aba_utilizada'],
                'linha_excel': d['linha_excel'],
            }
            codigos = []
            for n in config.CAMERAS:
                orig = d.get(f'Câmera {n}')
                it = interpretar_camera(orig)
                row[f'cam{n}_original'] = None if vazio(orig) else str(orig)
                row[f'cam{n}_codigo'] = it['codigo']
                row[f'cam{n}_classificacao'] = it['classificacao']
                row[f'cam{n}_erros'] = ', '.join(it['erros'])
                codigos.append(it['codigo'])
            row['codigos'] = ''.join(codigos)
            row['status_geral'] = status_geral(codigos)
            todos.append(row)
        info['datas_na_coluna'] = sorted(str(x) for x in datas_col)
        info['data_confere_com_nome'] = datas_col == {info['data_arquivo']}
        if not info['data_confere_com_nome']:
            info.setdefault('alertas', []).append('Data da coluna diverge da data do nome do arquivo')
    df = pd.DataFrame(todos)
    df['duplicado_prefixo_data'] = df.duplicated(['prefixo', 'data'], keep=False)
    return df, infos

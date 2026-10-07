"""Geração das bases tratadas (data/processed) e do JSON compacto do site (site/public/data)."""
import datetime as dt
import json
from collections import Counter, defaultdict

import pandas as pd

from . import config
from .config import rotulo_camera
from .interpretacao import NOME_STATUS, interpretar_camera

DIAS_SEMANA = ['seg', 'ter', 'qua', 'qui', 'sex', 'sáb', 'dom']


def _json(obj, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, separators=(',', ':'), default=str)


def _salvar(df, nome, xlsx=True):
    config.PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.PROCESSED / f'{nome}.csv', index=False, encoding='utf-8-sig')
    if xlsx:
        with pd.ExcelWriter(config.PROCESSED / f'{nome}.xlsx', engine='xlsxwriter') as w:
            df.to_excel(w, index=False, sheet_name=nome[:31])


def colunas_matriz(df, eventos):
    datas_arquivo = {}
    for d, a in df[['data', 'arquivo_origem']].drop_duplicates().itertuples(index=False):
        datas_arquivo[d] = a
    cols = []
    d = config.PERIODO_INICIO
    while d <= config.PERIODO_FIM:
        cols.append(d)
        d += dt.timedelta(days=1)
    extras = sorted({dt.date.fromisoformat(e['data']) for e in eventos if e['data'] and
                     dt.date.fromisoformat(e['data']) > config.PERIODO_FIM})
    out = []
    for d in cols + extras:
        out.append({'data': d.isoformat(), 'rotulo': d.strftime('%d/%m'), 'dia_semana': DIAS_SEMANA[d.weekday()],
                    'tem_arquivo': d in datas_arquivo, 'arquivo': datas_arquivo.get(d),
                    'fora_periodo': d > config.PERIODO_FIM})
    return out


def detectar_inconsistencias(df, infos, forms_info, forms, eventos, duplicados, reconc=None):
    inc = []
    if reconc is not None and len(reconc):
        for (emp, d, acao), g in reconc.groupby(['empresa', 'data', 'acao']):
            onde = f"{emp} em {dt.date.fromisoformat(d).strftime('%d/%m/%Y')}"
            if acao == 'REMAPEADO':
                mp = Counter(g['mapeamento'])
                inc.append({'tipo': 'Câmeras reconciliadas com o histórico (decisão 07/10/2026)', 'onde': onde,
                            'detalhe': f"{len(g)} veículo{'s' if len(g) != 1 else ''} com as posições ajustadas ao registro anterior: "
                                       + ', '.join(f'{m} ({n}×)' for m, n in mp.most_common()) + '. Valores apenas trocados de coluna.'})
            else:
                ex = ', '.join(str(p) for p in g['prefixo'][:15])
                inc.append({'tipo': 'Câmeras não reconciliadas (ambíguo)', 'onde': onde,
                            'detalhe': f'{len(g)} veículo{"s" if len(g) != 1 else ""} mantido{"s" if len(g) != 1 else ""} como no relatório ({"; ".join(sorted(set(g["motivo"])))}): {ex}{"…" if len(g) > 15 else ""}'})
    for i in infos:
        orig = [str(c) for c in i['colunas_originais']]
        esp = [c for c in orig if c != c.strip() or '  ' in c]
        if esp:
            inc.append({'tipo': 'Cabeçalho com espaço extra', 'onde': i['arquivo'], 'detalhe': ', '.join(repr(c) for c in esp) + ' → padronizado'})
        if 'Manutenção' not in [c.strip() for c in orig]:
            inc.append({'tipo': 'Coluna ausente', 'onde': i['arquivo'], 'detalhe': "Sem a coluna 'Manutenção'"})
        extras = [c for c in orig if c.strip() not in ('Prefixo', 'Data', 'Empresa', 'Status', 'Manutenção') and not c.strip().startswith('Câmera')]
        if extras:
            inc.append({'tipo': 'Coluna extra', 'onde': i['arquivo'], 'detalhe': ', '.join(extras)})
        if not i['data_confere_com_nome']:
            inc.append({'tipo': 'Data divergente', 'onde': i['arquivo'], 'detalhe': 'Data da coluna diferente do nome do arquivo'})
    emp_orig = sorted({e for e in df['empresa_original'].dropna() if isinstance(e, str) and e != e.strip()})
    if emp_orig:
        inc.append({'tipo': 'Empresa com espaço no final', 'onde': 'Relatórios CFTV', 'detalhe': ', '.join(repr(e) for e in emp_orig) + ' → padronizado'})
    # empresas ausentes em alguma data
    cont = df.groupby(['empresa', 'data']).size().unstack(fill_value=0)
    for emp, row in cont.iterrows():
        for d, n in row.items():
            if n == 0:
                inc.append({'tipo': 'Empresa ausente no arquivo', 'onde': f"Relatório CFTV de {d.strftime('%d/%m/%Y')}",
                            'detalhe': f'{emp}: nenhum registro nesta data (células em branco)'})
    # dias do período sem arquivo
    datas = set(df['data'])
    d = config.PERIODO_INICIO
    sem = []
    while d <= config.PERIODO_FIM:
        if d not in datas:
            sem.append(d.strftime('%d/%m') + f' ({DIAS_SEMANA[d.weekday()]})')
        d += dt.timedelta(days=1)
    if sem:
        inc.append({'tipo': 'Datas sem arquivo CFTV', 'onde': f'Período {config.PERIODO_INICIO:%d/%m}–{config.PERIODO_FIM:%d/%m}', 'detalhe': ', '.join(sem) + ' → colunas em branco'})
    # prefixos que mudam de empresa
    me = df.groupby('prefixo')['empresa'].nunique()
    if (me > 1).any():
        ex = ', '.join(str(p) for p in me[me > 1].index[:12])
        inc.append({'tipo': 'Prefixo muda de empresa', 'onde': 'Relatórios CFTV', 'detalhe': f'{int((me > 1).sum())} prefixos (ex.: {ex}…)'})
    # mudanças atípicas de padrão '-' (ex.: colunas trocadas) por empresa/data
    s = df.sort_values(['prefixo', 'data'])
    prev = s.groupby('prefixo')['codigos'].shift()
    trocas = Counter()
    for (emp, d, a, b) in zip(s['empresa'], s['data'], prev, s['codigos']):
        if isinstance(a, str):
            n = sum(1 for x, y in zip(a, b) if (x == '-') != (y == '-') and x != '.' and y != '.')
            if n:
                trocas[(emp, d)] += n
    for (emp, d), n in trocas.items():
        if n >= 50:
            inc.append({'tipo': "Mudança atípica no padrão de câmeras ('-')", 'onde': f"{emp} em {d.strftime('%d/%m/%Y')}",
                        'detalhe': f'{n} trocas entre "sem câmera" e câmera com valor em relação ao registro anterior (possível troca de colunas na exportação). Dado mantido como está.'})
    # mudança de grade (colunas vazias) por empresa
    s['grade'] = s['codigos'].map(lambda c: ''.join('.' if x == '.' else 'X' for x in c))
    moda = s.groupby('empresa')['grade'].agg(lambda x: x.mode().iloc[0])
    g = s.groupby(['empresa', 'data'])['grade'].agg(lambda x: x.mode().iloc[0])
    for (emp, d), gr in g.items():
        if gr != moda[emp]:
            inc.append({'tipo': 'Mudança na grade de colunas', 'onde': f"{emp} em {d.strftime('%d/%m/%Y')}",
                        'detalhe': f'{gr.count("X")} colunas de câmera preenchidas (normalmente {moda[emp].count("X")}).'})
    for p, d in duplicados:
        inc.append({'tipo': 'Duplicidade prefixo+data', 'onde': f'{p} em {d}', 'detalhe': 'mantida a pior situação para a cor'})
    textos = Counter()
    for n in config.CAMERAS:
        textos.update(df[f'cam{n}_codigo'][df[f'cam{n}_codigo'] == '?'].index.map(lambda i: df.at[i, f'cam{n}_original']))
    for t, c in textos.items():
        inc.append({'tipo': 'Texto de câmera não reconhecido', 'onde': 'Relatórios CFTV', 'detalhe': f'{t!r} ({c}×)'})
    for f in forms:
        for a in f['alertas']:
            inc.append({'tipo': 'Formulário de manutenção', 'onde': f"linha {f['linha_excel']} — prefixo {f['prefixo']}", 'detalhe': a})
    for e in eventos:
        if e['fora_periodo']:
            inc.append({'tipo': 'Manutenção fora do período CFTV', 'onde': f"prefixo {e['prefixo']} em {e['data']}", 'detalhe': 'coluna extra só com a bolinha; SEM DADOS PARA VALIDAR'})
    return inc


def montar_matriz(df, eventos):
    """Matriz do site: 1 item por prefixo; 1 posição por coluna (data). Sem registro -> ' ' (BRANCO / SEM DADOS)."""
    colunas = colunas_matriz(df, eventos)
    col_idx = {c['data']: i for i, c in enumerate(colunas)}
    ncol = len(colunas)
    empresas = sorted(df['empresa'].unique())
    emp_idx = {e: i for i, e in enumerate(empresas)}
    status_op = sorted(df['status_operacional_cftv'].dropna().unique())
    sop_idx = {s: i for i, s in enumerate(status_op)}
    manut_vals = sorted(df['ultima_manutencao_cftv'].dropna().unique())
    mv_idx = {v: i for i, v in enumerate(manut_vals)}

    ev_por_prefixo = defaultdict(list)
    for i, e in enumerate(eventos):
        ev_por_prefixo[e['prefixo']].append(i)

    prefixos = []
    df_s = df.sort_values(['prefixo', 'data'])
    for p, g in df_s.groupby('prefixo', sort=True):
        gs = [' '] * ncol
        ks = ['      '] * ncol
        ss = ['_'] * ncol
        rs = [0] * ncol
        us = [-1] * ncol
        es = [-1] * ncol
        for r in g.itertuples(index=False):
            j = col_idx.get(r.data.isoformat())
            if j is None:
                continue
            gs[j] = r.status_geral
            ks[j] = r.codigos
            ss[j] = chr(65 + sop_idx[r.status_operacional_cftv]) if r.status_operacional_cftv in sop_idx else '_'
            rs[j] = int(r.linha_excel)
            us[j] = mv_idx.get(r.ultima_manutencao_cftv, -1)
            es[j] = emp_idx[r.empresa]
        item = {'p': int(p), 'e': emp_idx[g['empresa'].iloc[-1]], 'g': ''.join(gs), 'k': ''.join(ks), 's': ''.join(ss), 'r': rs}
        if any(u >= 0 for u in us):
            item['u'] = us
        if len({x for x in es if x >= 0}) > 1:
            item['ed'] = es
        if p in ev_por_prefixo:
            item['m'] = ev_por_prefixo[p]
        prefixos.append(item)
    # prefixos só da manutenção (não existem no CFTV)
    no_cftv = sorted({e['prefixo'] for e in eventos} - set(df['prefixo']))
    for p in no_cftv:
        prefixos.append({'p': int(p), 'e': -1, 'g': ' ' * ncol, 'k': ' ' * 6 * ncol, 's': '_' * ncol, 'r': [0] * ncol,
                         'm': ev_por_prefixo[p], 'semCftv': True})
    prefixos.sort(key=lambda x: x['p'])
    return {'colunas': colunas, 'cameras': config.CAMERAS, 'posicoes': {str(k): v for k, v in config.POSICAO_DA_CAMERA.items()},
            'empresas': empresas, 'statusOp': status_op, 'manutCftv': manut_vals, 'prefixos': prefixos}


def gerar(df, infos, forms, forms_info, eventos, duplicados, sem_data, reconc=None):
    cftv_json = montar_matriz(df, eventos)

    # auditoria: textos originais -> interpretação
    cont_txt = Counter()
    for n in config.CAMERAS:
        cont_txt.update(df[f'cam{n}_original'].fillna('(vazio)'))
    auditoria_textos = []
    for t, c in cont_txt.most_common():
        it = interpretar_camera(None if t == '(vazio)' else t)
        auditoria_textos.append({'original': t, 'quantidade': c, **it})

    inc = detectar_inconsistencias(df, infos, forms_info, forms, eventos, duplicados, reconc)
    if reconc is not None:
        _salvar(reconc, 'reconciliacao_cameras')

    manut_json = {'forms': forms, 'eventos': eventos}
    meta = {
        'gerado_em': dt.datetime.now().strftime('%d/%m/%Y %H:%M'),
        'periodo': {'inicio': config.PERIODO_INICIO.isoformat(), 'fim': config.PERIODO_FIM.isoformat()},
        'arquivos_cftv': [{k: v for k, v in i.items() if k != 'colunas_originais'} | {'colunas_originais': [str(c) for c in i['colunas_originais']]} for i in infos],
        'arquivo_manutencao': forms_info,
        'auditoria_textos': auditoria_textos,
        'inconsistencias': inc,
        'formularios_sem_data': sem_data,
        'totais': {'registros_cftv': int(len(df)), 'prefixos_cftv': int(df['prefixo'].nunique()),
                   'formularios': len(forms), 'eventos': len(eventos)},
    }
    config.SITE_DATA.mkdir(parents=True, exist_ok=True)
    _json(cftv_json, config.SITE_DATA / 'cftv.json')
    _json(manut_json, config.SITE_DATA / 'manutencoes.json')
    _json(meta, config.SITE_DATA / 'meta.json')

    # ---------------- bases tratadas (data/processed) ----------------
    base = df.copy()
    base['data'] = base['data'].map(lambda d: d.isoformat())
    base['status_geral_nome'] = base['status_geral'].map(NOME_STATUS)
    for n in config.CAMERAS:
        base.insert(base.columns.get_loc(f'cam{n}_original'), f'cam{n}_posicao', config.POSICAO_DA_CAMERA[n])
    base = base.drop(columns=['codigos'])
    _salvar(base, 'cftv_consolidado')

    rows = []
    for f in forms:
        r = {'linha_excel': f['linha_excel'], 'prefixo': f['prefixo'], 'data': f['data'], 'hora': f['hora'],
             'data_texto_original': f['data_texto'], 'tecnico': f['tecnico'], 'tecnico_original': f['tecnico_original'],
             'id_formulario': f['id_formulario'], 'garagem': f['garagem'], 'tecnologia': f['tecnologia']}
        for pos in config.ORDEM_POSICOES:
            d = next((x for x in f['posicoes'] if x['posicao'] == pos), None)
            lab = rotulo_camera(config.CAMERA_DA_POSICAO[pos])
            r[f'{lab} — problemas'] = '\n'.join(d['problemas']) if d else None
            r[f'{lab} — ações'] = '\n'.join(d['acoes']) if d else None
        r['cameras_com_anomalia'] = ', '.join(rotulo_camera(c) for c in f['cameras_com_anomalia'])
        r['cameras_citadas_no_texto'] = ', '.join(rotulo_camera(c) for c in f['cameras_citadas_texto'])
        r['notacao_C_no_texto'] = ', '.join(f['notacao_c_texto'])
        r['pecas_equipamentos'] = '\n'.join(f['pecas'])
        for k, v in f['quantidades'].items():
            r[k] = v
        for k in ('instalado', 'retirado', 'nao_especificado'):
            r[f'serie_{k}'] = ', '.join(f['equipamento'][k]['series'])
            r[f'mac_{k}'] = ', '.join(f['equipamento'][k]['macs'])
        r['pendencia'] = 'SIM' if f['pendencia'] else 'NÃO'
        r['pendencia_trechos'] = '\n'.join(t['trecho'] for t in f['pendencia_trechos'])
        r['observacoes'] = f['observacoes']
        r['alertas'] = '\n'.join(f['alertas'])
        rows.append(r)
    _salvar(pd.DataFrame(rows), 'manutencoes_tratadas')

    rel, ana, reco = [], [], []
    for e in eventos:
        a, d = e['antes'], e['dia']
        rel.append({'evento': e['id'], 'prefixo': e['prefixo'], 'data_manutencao': e['data'], 'horas': ', '.join(e['horas']),
                    'formularios_linhas_excel': ', '.join(map(str, e['forms'])), 'tecnicos': ', '.join(e['tecnicos']),
                    'garagens': ', '.join(e['garagens']), 'prefixo_no_cftv': 'SIM' if e['prefixo_no_cftv'] else 'NÃO',
                    'antes_data': a and a['data'], 'antes_status': a and a['status_nome'],
                    'antes_problemas': a and '; '.join(p['rotulo'] + ' ' + p['descricao'] for p in a['problemas']),
                    'dia_status': d and d['status_nome'],
                    'depois_registros': len(e['depois']),
                    'depois_sequencia': ' | '.join(f"{x['data']} {x['status_nome']}" for x in e['depois']),
                    'janela_ate_exclusive': e['janela_fim']})
        n, p = e['normalizacao'] or {}, e['permanencia'] or {}
        da = e['duracao_antes'] or {}
        ana.append({'evento': e['id'], 'prefixo': e['prefixo'], 'data_manutencao': e['data'], 'resultado': e['resultado'],
                    'motivo': e['motivo'], 'pendencia': 'SIM' if e['pendencia'] else 'NÃO',
                    'veiculo_normal_antes': 'SIM' if e['veiculo_normal_antes'] else 'NÃO',
                    'cameras_problema_antes': ', '.join(rotulo_camera(c) for c in e['cameras_problema_antes']),
                    'cameras_citadas_formulario': ', '.join(rotulo_camera(c) for c in e['cameras_formulario']),
                    'problema_desde': da.get('primeiro_dia'), 'registros_com_problema_antes': da.get('registros_com_problema'),
                    'dias_corridos_com_problema_antes': da.get('dias_corridos'),
                    'normalizou': ('SIM' if n.get('normalizou') else ('NÃO' if n else None)),
                    'primeiro_registro_normal': n.get('primeiro_normal'), 'registros_ate_normalizar': n.get('registros_ate_normalizar'),
                    'dias_corridos_ate_normalizar': n.get('dias_ate_normalizar'),
                    'registros_normais_depois': p.get('registros_normais'), 'dias_corridos_normais_depois': p.get('dias_corridos'),
                    'problema_voltou': 'SIM' if e['recorrencia'] else ('NÃO' if n.get('normalizou') else None),
                    'data_recorrencia': e['recorrencia'] and e['recorrencia']['data'],
                    'camera_recorrencia': e['recorrencia'] and ', '.join(x['rotulo'] for x in e['recorrencia']['problemas']),
                    'novo_problema_outra_camera_data': e['novo_problema_outra_camera'] and e['novo_problema_outra_camera']['data'],
                    'novo_problema_outra_camera': e['novo_problema_outra_camera'] and '; '.join(x['rotulo'] + ' ' + x['descricao'] for x in e['novo_problema_outra_camera']['problemas']),
                    'historia': '\n'.join(e['historia'])})
        if e['recorrencia']:
            for x in e['recorrencia']['problemas']:
                reco.append({'evento': e['id'], 'prefixo': e['prefixo'], 'data_manutencao': e['data'], 'tipo': 'RECORRÊNCIA NA MESMA CÂMERA',
                             'data': e['recorrencia']['data'], 'camera': x['rotulo'], 'situacao': x['descricao']})
        if e['novo_problema_outra_camera']:
            for x in e['novo_problema_outra_camera']['problemas']:
                reco.append({'evento': e['id'], 'prefixo': e['prefixo'], 'data_manutencao': e['data'], 'tipo': 'NOVO PROBLEMA EM OUTRA CÂMERA (não é recorrência)',
                             'data': e['novo_problema_outra_camera']['data'], 'camera': x['rotulo'], 'situacao': x['descricao']})
    _salvar(pd.DataFrame(rel), 'manutencao_x_cftv')
    _salvar(pd.DataFrame(ana), 'analise_antes_depois')
    _salvar(pd.DataFrame(reco, columns=['evento', 'prefixo', 'data_manutencao', 'tipo', 'data', 'camera', 'situacao']), 'recorrencias')
    _salvar(pd.DataFrame([{'arquivo': i['arquivo'], 'abas': ', '.join(i['abas']), 'aba_utilizada': i['aba_utilizada'],
                           'abas_ignoradas': '; '.join(f"{x['aba']} ({x['motivo']})" for x in i['abas_ignoradas']),
                           'registros': i['registros'], 'data_confere_com_nome': i['data_confere_com_nome']} for i in infos]
                         + [{'arquivo': forms_info['arquivo'], 'abas': ', '.join(forms_info['abas']), 'aba_utilizada': forms_info['aba_utilizada'],
                             'abas_ignoradas': '; '.join(f"{x['aba']} ({x['motivo']})" for x in forms_info['abas_ignoradas']),
                             'registros': forms_info['registros'], 'data_confere_com_nome': None}]), 'resumo_arquivos', xlsx=False)
    _salvar(pd.DataFrame(inc), 'inconsistencias', xlsx=False)
    return cftv_json, manut_json, meta

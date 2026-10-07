"""Reconciliação das posições de câmera com o histórico do veículo — decisão da Letícia em 07/10/2026
(REGRAS_PROJETO.md §17-A). Exceção à estabilidade do '-' por prefixo/câmera (§15) e à Q19 só para as datas a partir
de config.RECONCILIAR_A_PARTIR: as posições são ajustadas ao histórico, sem descartar a leitura nova.

Regra determinística, para cada registro com data >= RECONCILIAR_A_PARTIR:
- câmeras existentes = colunas com valor (código diferente de '-' sem câmera e de '.' fora da grade);
- histórico = câmeras existentes no registro anterior mais recente do mesmo prefixo (já reconciliado, se for o caso);
- sem registro anterior (veículo novo) -> mantém como está no relatório;
- mesmas câmeras do histórico -> nada muda;
- mesma QUANTIDADE e números diferentes -> mapeamento posicional, em ordem crescente: a k-ésima câmera de agora vai
  para a k-ésima câmera do histórico (ex.: só 'Câmera 22' agora e só 21 antes -> o valor passa para a Câmera 21).
  As demais colunas (sem câmera/fora da grade) ocupam as colunas que sobraram, também em ordem crescente, de modo que
  é só uma troca de lugar: nenhum valor é criado, apagado ou alterado;
- quantidade diferente (ou nenhuma câmera agora) -> ambíguo: mantém o valor original e lista o veículo.
O registro guarda as colunas de origem em 'cameras_reconciliadas' (ex.: 'Câmera 22→21') e o motivo em
'reconciliacao' (rastreabilidade). Os arquivos de data/raw não são alterados.
"""
import pandas as pd

from . import config

CAMPOS = ('original', 'codigo', 'classificacao', 'erros')
AUSENTE = ('-', '.')


def _existentes(row):
    return [n for n in config.CAMERAS if row[f'cam{n}_codigo'] not in AUSENTE]


def reconciliar(df: pd.DataFrame):
    """Retorna (df reconciliado, DataFrame com o relatório de reconciliação: 1 linha por registro avaliado com conflito)."""
    df = df.copy()
    df['cameras_reconciliadas'] = None
    df['reconciliacao'] = None
    corte = config.RECONCILIAR_A_PARTIR
    if corte is None:
        return df, pd.DataFrame()
    df = df.sort_values(['prefixo', 'data', 'arquivo_origem', 'linha_excel']).reset_index(drop=True)
    ultimo = {}   # prefixo -> câmeras existentes no registro mais recente já processado
    rel = []
    for i in df.index:
        row = df.loc[i]
        p, agora = row['prefixo'], _existentes(row)
        if row['data'] >= corte:
            hist = ultimo.get(p)
            base = {'prefixo': int(p), 'data': row['data'].isoformat(), 'empresa': row['empresa'],
                    'arquivo_origem': row['arquivo_origem'], 'linha_excel': int(row['linha_excel']),
                    'cameras_relatorio': ', '.join(map(str, agora)) or '(nenhuma)',
                    'cameras_historico': None if hist is None else (', '.join(map(str, hist)) or '(nenhuma)')}
            if hist is not None and agora != hist:
                if len(agora) == len(hist) and agora:
                    resto_a = [n for n in config.CAMERAS if n not in agora]
                    resto_h = [n for n in config.CAMERAS if n not in hist]
                    mapa = dict(zip(agora + resto_a, hist + resto_h))   # coluna de origem -> coluna de destino
                    valores = {n: {c: row[f'cam{n}_{c}'] for c in CAMPOS} for n in config.CAMERAS}
                    for o, d in mapa.items():
                        for c in CAMPOS:
                            df.at[i, f'cam{d}_{c}'] = valores[o][c]
                    df.at[i, 'codigos'] = ''.join(df.at[i, f'cam{n}_codigo'] for n in config.CAMERAS)
                    txt = '; '.join(f'Câmera {a}→{h}' for a, h in zip(agora, hist))
                    df.at[i, 'cameras_reconciliadas'] = txt
                    df.at[i, 'reconciliacao'] = 'posições ajustadas ao histórico (decisão 07/10/2026)'
                    rel.append({**base, 'acao': 'REMAPEADO', 'mapeamento': txt, 'motivo': 'mesma quantidade de câmeras do histórico'})
                    agora = hist
                else:
                    motivo = (f'quantidade diferente do histórico ({len(agora)} agora × {len(hist)} antes)'
                              if len(agora) != len(hist) else 'nenhuma câmera no relatório')
                    df.at[i, 'reconciliacao'] = f'mantido como no relatório: {motivo}'
                    rel.append({**base, 'acao': 'MANTIDO (ambíguo)', 'mapeamento': None, 'motivo': motivo})
        ultimo[p] = agora
    return df, pd.DataFrame(rel, columns=['prefixo', 'data', 'empresa', 'arquivo_origem', 'linha_excel', 'cameras_relatorio',
                                          'cameras_historico', 'acao', 'mapeamento', 'motivo'])

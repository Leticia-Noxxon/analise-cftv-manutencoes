import os, collections
import pandas as pd
P = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', '_cftv_raw_concat.pkl')
df = pd.read_pickle(P)
cams = [f'Câmera {n}' for n in range(21, 27)]
def kind(v):
    if v is None or (isinstance(v, float) and pd.isna(v)): return 'VAZIO'
    if v == '-': return '-'
    if v == 'OFFLINE': return 'OFF'
    if 'error' in v: return 'ERR'
    if v.startswith('ONLINE'): return 'OK'
    return 'OUTRO:' + v
for c in cams: df['k' + c[-2:]] = df[c].map(kind)
K = ['k' + c[-2:] for c in cams]
# padrao de colunas vazias (quantidade de câmeras na grade)
df['ncols'] = df[K].apply(lambda r: sum(x != 'VAZIO' for x in r), axis=1)
df['vazio_pat'] = df[K].apply(lambda r: ''.join('.' if x == 'VAZIO' else 'X' for x in r), axis=1)
print('padrões de células vazias (X=preenchida):'); print(df['vazio_pat'].value_counts().to_string())
g = df.groupby('Prefixo')['vazio_pat'].nunique()
print('prefixos com padrão de vazio variável entre dias:', (g > 1).sum(), 'de', len(g))
# '-' constante?
for c in K:
    s = df.groupby('Prefixo')[c].agg(lambda x: set(x))
    has_dash = s[s.map(lambda x: '-' in x)]
    always = has_dash[has_dash.map(lambda x: x == {'-'})]
    print(c, 'prefixos com "-":', len(has_dash), ' sempre "-":', len(always), ' às vezes:', len(has_dash) - len(always))
# exemplos de variação
s = df.groupby('Prefixo')['k21'].agg(lambda x: set(x))
ex = s[s.map(lambda x: '-' in x and len(x) > 1)].head(5).index
for p in ex:
    print(df.loc[df.Prefixo == p, ['Data', 'Empresa'] + cams[:3] + ['Status']].to_string())
# prefixos com todas '-'
df['n_dash'] = df[K].apply(lambda r: sum(x == '-' for x in r), axis=1)
df['n_real'] = df[K].apply(lambda r: sum(x in ('OK', 'ERR', 'OFF') for x in r), axis=1)
print('linhas sem nenhuma câmera real (tudo - / vazio):', (df.n_real == 0).sum())
print(df.loc[df.n_real == 0, 'Status'].value_counts().to_string())
# Status vs combinação
def combo(r):
    ks = [x for x in r if x in ('OK', 'ERR', 'OFF', '-')]
    return ('OFF' if 'OFF' in ks else '') + ('ERR' if 'ERR' in ks else '') + ('OK' if 'OK' in ks else '') + ('-' if '-' in ks else '')
df['combo'] = df[K].apply(combo, axis=1)
print(pd.crosstab(df['Status'], df['combo']).to_string())
# 100% Offline: todas as reais OFF?
x = df[df.Status == '100% Offline']
print('100% Offline: todas reais OFF', ((x[K] == 'OFF').sum(axis=1) == x.n_real).mean())
# Empresa por prefixo
e = df.groupby('Prefixo')['Empresa'].nunique()
print('prefixos com >1 empresa:', (e > 1).sum())
print(df[df.Prefixo.isin(e[e > 1].index)].groupby('Prefixo')['Empresa'].agg(lambda x: sorted(set(x))).head(20).to_string())
# Manutenção: constante por prefixo?
def mk(v):
    if isinstance(v, str): return v
    if v is None or (isinstance(v, float) and pd.isna(v)): return 'AUSENTE'
    return v.strftime('%Y-%m-%d')
df['mk'] = df['Manutenção'].map(mk)
mm = df[df.mk != 'AUSENTE'].groupby('Prefixo')['mk'].nunique()
print('Manutenção: prefixos com 1 valor', (mm == 1).sum(), ' >1 valor', (mm > 1).sum())
ex = mm[mm > 1].head(5).index
for p in ex: print(p, df.loc[df.Prefixo == p, ['Data', 'mk', 'Status']].values.tolist())
# datas de manutenção em setembro — comparação com a data do arquivo
sep = df[df.mk.str.startswith('2026-09')]
print('Manutenção em set: pares (mk, data_arquivo) — mk > data arquivo?', (pd.to_datetime(sep.mk) > sep.data_arquivo).sum())
# prefixos por arquivo: presença
pres = df.groupby('Prefixo')['data_arquivo'].nunique()
print('prefixos por nº de dias presentes:'); print(pres.value_counts().sort_index().to_string())
# linhas vazias no meio?
df.to_pickle(P.replace('_cftv_raw_concat', '_cftv_kinds'))

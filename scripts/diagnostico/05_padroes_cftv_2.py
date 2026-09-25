import os
import pandas as pd
P = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', '_cftv_kinds.pkl')
df = pd.read_pickle(P)
K = ['k21','k22','k23','k24','k25','k26']
print('Empresa repr:', sorted(df['Empresa'].map(repr).unique()))
e04 = set(df[df.data_arquivo=='2026-09-04'].Empresa.str.strip()); eall = set(df.Empresa.str.strip())
print('empresa ausente em 04/09:', eall - e04)
print('registros por empresa por dia:'); print(pd.crosstab(df.Empresa.str.strip(), df.data_arquivo.dt.strftime('%d')).to_string())
print('Prefixo min/max', df.Prefixo.min(), df.Prefixo.max())
print('dias da semana:', sorted(set((d.strftime('%d/%m %a')) for d in df.data_arquivo)))
# câmeras com valor real por prefixo (em algum dia)
real = df[K].isin(['OK','ERR','OFF'])
df['cams_reais'] = real.apply(lambda r: ','.join(k[1:] for k, v in zip(K, r) if v), axis=1)
per = df.groupby('Prefixo')['cams_reais'].agg(lambda x: set(x))
print('conjuntos de câmeras reais por prefixo — prefixos com conjunto constante:', (per.map(len)==1).sum(), 'variável:', (per.map(len)>1).sum())
print(df['cams_reais'].value_counts().to_string())
# empresas x grade
print(pd.crosstab(df.Empresa.str.strip(), df.vazio_pat).to_string())
# '-' x empresa
df['tem_dash'] = df[K].eq('-').any(axis=1)
print(pd.crosstab(df.Empresa.str.strip(), df.tem_dash).to_string())
# variações '-' <-> real: com o que alterna?
import collections
trans = collections.Counter()
d2 = df.sort_values(['Prefixo','data_arquivo'])
for k in K:
    prev = d2.groupby('Prefixo')[k].shift()
    m = prev.notna() & (prev != d2[k]) & ((prev == '-') | (d2[k] == '-'))
    trans.update(zip(prev[m], d2[k][m]))
print('transições envolvendo "-" entre dias consecutivos disponíveis:', trans.most_common())
# Status 'Câmera Inexistente' amostra
print(df[df.Status=='Câmera Inexistente'][['Prefixo','Data','Empresa','Câmera 21','Câmera 22','Câmera 23','Câmera 24','Câmera 25','Câmera 26']].head(8).to_string())
# linhas vazias no meio da planilha?
for f, g in df.groupby('arquivo_origem'):
    le = g.linha_excel.values
    gaps = (le[1:] - le[:-1] > 1).sum()
    print(f, 'última linha', le.max(), 'saltos', gaps)

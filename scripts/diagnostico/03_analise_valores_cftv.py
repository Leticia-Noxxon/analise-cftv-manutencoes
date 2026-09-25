import os, re, collections
import pandas as pd
P = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', '_cftv_raw_concat.pkl')
df = pd.read_pickle(P)
cams = [f'Câmera {n}' for n in range(21, 27)]
print('colunas', list(df.columns))
print('\n== Empresa ==')
print(df['Empresa'].value_counts(dropna=False).to_string())
print('\nEmpresas por arquivo (nunique):', df.groupby('arquivo_origem')['Empresa'].nunique().to_dict())
print('\n== Status ==')
print(df['Status'].value_counts(dropna=False).to_string())
print('\n== Manutenção (tipos) ==')
print(df['Manutenção'].map(lambda x: type(x).__name__).value_counts(dropna=False).to_string())
m = df['Manutenção']
print(m[m.map(lambda x: isinstance(x, str))].value_counts().head(40).to_string())
dt = m[m.map(lambda x: hasattr(x, 'year'))]
print('datas manutenção min/max', dt.min(), dt.max(), 'n', len(dt), 'unique', dt.nunique())
print(pd.Series(dt).map(lambda x: x.strftime('%Y-%m')).value_counts().sort_index().to_string())
print('\n== Valores de câmeras ==')
vals = collections.Counter()
for c in cams:
    vals.update(df[c].map(lambda v: repr(v) if not isinstance(v, str) else v))
for k, v in vals.most_common():
    print(f'{v:8d}  {k}')
print('\nPor coluna:')
for c in cams:
    s = df[c]
    print(c, 'None', s.isna().sum(), '-', (s == '-').sum(), 'OFFLINE', (s == 'OFFLINE').sum(), 'ONLINE*', s.astype(str).str.startswith('ONLINE').sum())
print('\n== Última Transmissão (01/09) ==')
u = df.loc[df['Última Transmissão'].notna(), 'Última Transmissão']
print(u.map(lambda x: type(x).__name__).value_counts().to_string())
print(u.astype(str).head(10).tolist())
print('Ult transm nula no arquivo 01/09:', df.loc[df.arquivo_origem.str.contains('01.09'), 'Última Transmissão'].isna().sum())
print(df.loc[df.arquivo_origem.str.contains('01.09')].groupby(df['Última Transmissão'].isna())['Status'].value_counts().to_string())

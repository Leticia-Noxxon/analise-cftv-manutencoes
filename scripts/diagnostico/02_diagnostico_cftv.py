import sys, os, re, collections, pickle
sys.path.insert(0, os.path.dirname(__file__))
import pandas as pd
from cftv_loader import load_all
dfs, infos = load_all()
out = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', '_cftv_raw_concat.pkl')
allc = pd.concat(dfs, ignore_index=True)
allc.to_pickle(out)
for d, i in zip(dfs, infos):
    print(i['arquivo'], '| abas', i['abas'], '| usada', i['aba_usada'], '| registros', len(d), '| vazias', i['linhas_vazias_ignoradas'])
    print('   cols orig', i['colunas_originais'])
    print('   Data unique', d['Data'].map(repr).value_counts().to_dict(), ' data_arquivo', d['data_arquivo'].iloc[0])
    print('   Prefixo types', d['Prefixo'].map(lambda x: type(x).__name__).value_counts().to_dict(), 'nunique', d['Prefixo'].nunique(), 'dups', d['Prefixo'].duplicated().sum(), 'null', d['Prefixo'].isna().sum())
print('TOTAL', len(allc), 'prefixos unicos', allc['Prefixo'].nunique())

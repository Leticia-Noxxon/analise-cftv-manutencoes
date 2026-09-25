import os
import pandas as pd
D = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
m = pd.read_pickle(os.path.join(D, '_manut_parsed.pkl'))
c = pd.read_pickle(os.path.join(D, '_cftv_kinds.pkl'))
dias_cftv = sorted(c.data_arquivo.unique())
m['dia'] = m['dt'].dt.normalize()
m['dia_tem_arquivo'] = m.dia.isin(dias_cftv)
print('manutenções por dia com/sem arquivo CFTV:'); print(m.groupby([m.dia.dt.strftime('%d/%m'), 'dia_tem_arquivo']).size().to_string())
pres = set(zip(c.Prefixo, c.data_arquivo))
m['registro_no_dia'] = [ (p, d) in pres for p, d in zip(m.Prefixo, m.dia)]
def antes(p, d): return any((p, x) in pres for x in dias_cftv if x < d)
def depois(p, d): return sum((p, x) in pres for x in dias_cftv if x > d)
m['tem_antes'] = [antes(p, d) for p, d in zip(m.Prefixo, m.dia)]
m['n_depois'] = [depois(p, d) for p, d in zip(m.Prefixo, m.dia)]
print('com registro CFTV no dia:', m.registro_no_dia.sum(), '/', len(m))
print('com registro anterior:', m.tem_antes.sum(), '| sem registro posterior (SEM DADOS PARA VALIDAR potencial):', (m.n_depois == 0).sum())
print('distribuição nº registros posteriores:', m.n_depois.value_counts().sort_index().to_dict())
print('Técnicos:', m.Nome.value_counts().to_dict())
print('Garagens:', m.Garagem.value_counts().to_dict())
# dump integral
with open(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', '_manutencao_registros_completos.txt'), 'w', encoding='utf-8') as f:
    cols = [x for x in m.columns if x not in ('dt','wd_ok','dia','empresa_cftv','grade','cams_reais','dia_tem_arquivo','registro_no_dia','tem_antes','n_depois')]
    for _, r in m.iterrows():
        f.write('=' * 100 + '\n')
        for col in cols:
            v = r[col]
            if v is None or (isinstance(v, float) and pd.isna(v)): continue
            f.write(f'[{col}]\n{v}\n')

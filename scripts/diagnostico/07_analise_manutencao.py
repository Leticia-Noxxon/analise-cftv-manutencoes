import os, re
import pandas as pd
D = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
m = pd.read_pickle(os.path.join(D, '_manut_raw.pkl'))
c = pd.read_pickle(os.path.join(D, '_cftv_kinds.pkl'))
MESES = {'janeiro':1,'fevereiro':2,'março':3,'abril':4,'maio':5,'junho':6,'julho':7,'agosto':8,'setembro':9,'outubro':10,'novembro':11,'dezembro':12}
rx = re.compile(r'^(\S+-feira|sábado|domingo), (\w+) (\d{1,2}), (\d{4}) (\d{2}):(\d{2})$')
def parse(s):
    mm = rx.match(s.strip())
    if not mm: return pd.NaT
    return pd.Timestamp(int(mm.group(4)), MESES[mm.group(2).lower()], int(mm.group(3)), int(mm.group(5)), int(mm.group(6)))
m['dt'] = m['Data'].map(parse)
print('datas não parseadas:', m['dt'].isna().sum(), m.loc[m.dt.isna(), 'Data'].tolist())
# checar dia da semana coerente
wd = ['segunda-feira','terça-feira','quarta-feira','quinta-feira','sexta-feira','sábado','domingo']
m['wd_ok'] = m.apply(lambda r: r['Data'].split(',')[0] == wd[r['dt'].weekday()], axis=1)
print('dia da semana incoerente:', (~m.wd_ok).sum())
print('min/max', m.dt.min(), m.dt.max())
print('por dia:'); print(m.dt.dt.strftime('%d/%m %a').value_counts().sort_index().to_string())
print('horas:'); print(m.dt.dt.hour.value_counts().sort_index().to_string())
# prefixos x CFTV
cp = set(c.Prefixo)
mp = set(m.Prefixo)
print('prefixos manutenção', len(mp), 'no CFTV', len(mp & cp), 'fora do CFTV', sorted(mp - cp))
# duplicados
dup = m[m.duplicated('Prefixo', keep=False)].sort_values(['Prefixo', 'dt'])
print('prefixos repetidos', dup.Prefixo.nunique())
print(dup[['linha_excel','Prefixo','Nome','Data','ID','Garagem']].to_string())
m['dia'] = m.dt.dt.normalize()
print('mesmo prefixo+mesmo dia:', m.duplicated(['Prefixo','dia'], keep=False).sum())
full_dup_cols = [x for x in m.columns if x not in ('linha_excel','dt','wd_ok','dia')]
print('linhas totalmente idênticas:', m.duplicated(full_dup_cols, keep=False).sum())
print(m[m.duplicated(full_dup_cols, keep=False)][['linha_excel','Prefixo','Nome','Data','ID']].to_string())
# ID
g = m.groupby('ID')['Prefixo'].nunique()
print('IDs usados por >1 prefixo:', g[g>1].to_dict())
g2 = m.groupby('Prefixo')['ID'].nunique()
print('prefixos com >1 ID:', g2[g2>1].to_dict())
print('Linhas com ID 32500 — técnicos:', m[m.ID==32500].Nome.value_counts().to_dict(), 'garagens', m[m.ID==32500].Garagem.value_counts().to_dict())
# Garagem manutenção x empresa CFTV
K=['k21','k22','k23','k24','k25','k26']
c['cams_reais'] = c[K].isin(['OK','ERR','OFF']).apply(lambda r: ','.join(k[1:] for k, v in zip(K, r) if v), axis=1)
last = c.sort_values('data_arquivo').groupby('Prefixo').tail(1).set_index('Prefixo')
m['empresa_cftv'] = m.Prefixo.map(last.Empresa.str.strip())
print(pd.crosstab(m.Garagem, m.empresa_cftv.fillna('(fora CFTV)')).to_string())
# Tecnologia x grade CFTV
m['grade'] = m.Prefixo.map(last.vazio_pat)
m['cams_reais'] = m.Prefixo.map(last.cams_reais)
print(pd.crosstab(m.Tecnologia, m.cams_reais.fillna('?')).to_string())
m.to_pickle(os.path.join(D, '_manut_parsed.pkl'))

# 11435
print(m[m.Prefixo==11435][['linha_excel','Nome','Data','Garagem','Tecnologia','Observações']].to_string())
# CFTV coluna Manutenção vs data do formulário
c['mk'] = c['Manutenção'].map(lambda v: v.strftime('%Y-%m-%d') if hasattr(v,'year') else (v if isinstance(v,str) else None))
res=[]
for _, r in m.iterrows():
    sub = c[(c.Prefixo==r.Prefixo)]
    vals = sorted(set(x for x in sub.mk.dropna() if x!='#N/A'))
    res.append((r.Prefixo, r['dt'].strftime('%Y-%m-%d'), vals[-3:]))
match = sum(1 for p,d,v in res if d in v)
print('manutenções do formulário cuja data aparece na coluna Manutenção do CFTV:', match, 'de', len(res))
import collections
delta = collections.Counter()
for p,d,v in res:
    if v:
        best = min(v, key=lambda x: abs((pd.Timestamp(x)-pd.Timestamp(d)).days))
        delta[(pd.Timestamp(best)-pd.Timestamp(d)).days]+=1
    else: delta['sem data']+=1
print('diferença (dias) entre data CFTV-Manutenção mais próxima e data do formulário:', sorted(delta.items(), key=lambda x: (isinstance(x[0],str), x[0])))
# relação hora x diferença
rows=[]
for (p,d,v),(_, r) in zip(res, m.iterrows()):
    dd = None
    if v:
        best = min(v, key=lambda x: abs((pd.Timestamp(x)-pd.Timestamp(d)).days)); dd=(pd.Timestamp(best)-pd.Timestamp(d)).days
    rows.append((r['dt'].hour, 'D-1' if dd==-1 else ('D0' if dd==0 else 'outro')))
x = pd.DataFrame(rows, columns=['hora','rel'])
print(pd.crosstab(x.hora, x.rel).to_string())

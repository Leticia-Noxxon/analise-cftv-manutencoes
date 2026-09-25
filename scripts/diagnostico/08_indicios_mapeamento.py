"""Investiga se há correspondência confiável entre 'Câmera 21..26' (CFTV) e posições (Frontal/Frente/Corredor N) do formulário.
Somente leitura / relatório de indícios — NÃO cria mapeamento."""
import os, re
import pandas as pd
D = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
m = pd.read_pickle(os.path.join(D, '_manut_parsed.pkl'))
c = pd.read_pickle(os.path.join(D, '_cftv_kinds.pkl'))
POS = ['Frontal', 'Frente', 'Corredor 1', 'Corredor 2', 'Corredor 3', 'Corredor 4']
PCOL = {p: f'Problemas Detectados: Câm. {p}' for p in POS}
ACOL = {p: f'Ações: Câm. {p}' for p in POS}
m['pos_preenchidas'] = m.apply(lambda r: ','.join(p for p in POS if pd.notna(r[PCOL[p]])), axis=1)
print(pd.crosstab(m.pos_preenchidas, m.Tecnologia).to_string())
def probl(r):
    out=[]
    for p in POS:
        v = r[PCOL[p]]
        if pd.notna(v) and v.strip() != 'Nenhuma anomalia identificada': out.append(p)
    return out
m['pos_com_problema'] = m.apply(probl, axis=1)
rx = re.compile(r'(?i)\b(?:c[aâ]m(?:era)?s?\.?\s*|c)(2[1-6]|[1-6])\b')
rx_num = re.compile(r'(?i)c[aâ]m(?:era|eras)?\.?\s*((?:2[1-6])(?:\s*(?:,|e|/)\s*2[1-6])*)')
def mentions(t):
    if not isinstance(t, str): return []
    nums = set()
    for g in rx_num.findall(t):
        nums.update(re.findall(r'2[1-6]', g))
    return sorted(nums)
m['cams_mencionadas'] = m['Observações'].map(mentions)
sub = m[m.cams_mencionadas.map(len) > 0]
print('\nregistros com Observações citando câmera 21-26:', len(sub))
last = c.sort_values('data_arquivo').groupby('Prefixo').tail(1).set_index('Prefixo')
for _, r in sub.iterrows():
    print('-' * 80)
    print(f"linha {r.linha_excel} | prefixo {r.Prefixo} | {r.Tecnologia} | CFTV cams reais últ. dia: {last.loc[r.Prefixo, ['k21','k22','k23','k24','k25','k26']].tolist() if r.Prefixo in last.index else 'n/d'}")
    print('  citadas:', r.cams_mencionadas, '| posições com problema:', r.pos_com_problema)
    for p in r.pos_com_problema: print(f'    {p}: {r[PCOL[p]]!r} -> {r[ACOL[p]]!r}')
    print('  OBS:', repr(r['Observações']))
print('\n\n==== TESTE: registros com exatamente 1 câmera citada e exatamente 1 posição com problema ====')
one = m[(m.cams_mencionadas.map(len) == 1) & (m.pos_com_problema.map(len) == 1)]
t = pd.crosstab([one.Tecnologia, one.cams_mencionadas.map(lambda x: 'Câmera ' + x[0])], one.pos_com_problema.map(lambda x: x[0]))
print(t.to_string())
print('\n==== mesmo nº de câmeras citadas e posições com problema (pares por ordem) ====')
eq = m[(m.cams_mencionadas.map(len) > 1) & (m.cams_mencionadas.map(len) == m.pos_com_problema.map(len))]
from collections import Counter
cnt = Counter()
for _, r in eq.iterrows():
    for a, b in zip(r.cams_mencionadas, r.pos_com_problema): cnt[(r.Tecnologia, a, b)] += 1
for k, v in sorted(cnt.items()): print(v, k)
print('\n==== Checagem de contradições da hipótese 21=Frontal,22=Frente,23=Corredor 1,24=Corredor 2,25=Corredor 3,26=Corredor 4 ====')
H = {'21':'Frontal','22':'Frente','23':'Corredor 1','24':'Corredor 2','25':'Corredor 3','26':'Corredor 4'}
tot=ok_prob=ok_fill=vazio=0; exemplos=[]
for _, r in sub.iterrows():
    for n in r.cams_mencionadas:
        tot+=1; p=H[n]
        if p in r.pos_com_problema: ok_prob+=1
        elif pd.notna(r[PCOL[p]]): ok_fill+=1; exemplos.append((r.linha_excel, n, p, r[PCOL[p]]))
        else: vazio+=1; exemplos.append((r.linha_excel, n, p, 'COLUNA VAZIA'))
print(f'menções: {tot} | posição inferida com problema: {ok_prob} | posição preenchida "sem anomalia": {ok_fill} | posição vazia: {vazio}')
for e in exemplos: print('  ', e)
# CFTV: nº de câmeras reais x Tecnologia (grade)

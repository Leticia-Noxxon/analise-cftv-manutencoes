import os, re
import pandas as pd
D = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
m = pd.read_pickle(os.path.join(D, '_manut_parsed.pkl'))
o = m['Observações'].fillna('')
def show(label, pat):
    mask = o.str.contains(pat, case=False, regex=True)
    print(f'\n### {label}: {mask.sum()} registros  (regex {pat})')
    for _, r in m[mask].iterrows():
        print(f"  [linha {r.linha_excel} | {r.Prefixo}] {r['Observações']!r}")
show('Serial / nº de série', r'n[úu]mero de s[ée]rie|serial|\bS/?N\b|\b[0-9A-Z]{18,}\b')
show('MAC', r'\bMAC\b')
show('Retirada / instalada', r'retirad|instalad')
show('Pendência / aguardando / falta / retorno', r'pend|aguard|falt|retorn|encaminh|n[ãa]o foi poss|sem sucesso|precis|necessit|agend')
show('Corredor sem número / C1..C6', r'corredor(?!\s*\d)|\bC[1-6]\b')
show('pen drive / UCP / DVR / TDM', r'pen ?drive|\bUCP\b|\bDVR\b|\bNVR\b|\bTDM\b')
print('\nObservações: comprimento máx', o.str.len().max(), 'com quebra de linha', o.str.contains('\n').sum())
print('Câmera/Switch/Cartão utilizados x ações:')
for col, pat in [('Câmera Utilizada', 'Substituição da câmera'), ('Switch Utilizado', 'Substituição do switch'), ('Cartão de Memória Utilizado', 'cartão de memória')]:
    acts = m[[x for x in m.columns if x.startswith('Ações')]].fillna('').agg('\n'.join, axis=1).str.contains(pat, case=False)
    print(' ', col, pd.crosstab(m[col].fillna('vazio'), acts).to_dict())
print('\n### Números de 5 dígitos nas Observações diferentes do Prefixo (possível prefixo divergente)')
c = pd.read_pickle(os.path.join(D, '_cftv_kinds.pkl')); cp = set(c.Prefixo)
for _, r in m.iterrows():
    nums = [int(x) for x in re.findall(r'(?<![\dA-Z])(\d{5})(?![\dA-Z])', r['Observações'] or '')] if isinstance(r['Observações'], str) else []
    diff = [n for n in nums if n != r.Prefixo and n != r.ID]
    if diff:
        print(f"  linha {r.linha_excel} | Prefixo col={r.Prefixo} | ID={r.ID} | números no texto≠prefixo: {diff} (no CFTV: {[n in cp for n in diff]}) | {r['Observações'][:120]!r}")

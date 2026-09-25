"""Gera tabela markdown por arquivo (usada no DIAGNOSTICO.md)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import pandas as pd
from cftv_loader import list_cftv_files, load_file
print('| # | Arquivo | Abas existentes | Aba utilizada | Aba ignorada | Registros | Linhas vazias ao final | Data (coluna) | Data = nome? | Prefixos únicos | Colunas diferentes do padrão |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
PAD = ['Prefixo','Data','Empresa','Câmera 21','Câmera 22','Câmera 23','Câmera 24','Câmera 25','Câmera 26','Status','Manutenção']
for i, f in enumerate(list_cftv_files(), 1):
    df, info = load_file(f)
    datas = sorted(set(df['Data']))
    ok = all(d == df['data_arquivo'].iloc[0] for d in datas)
    orig = info['colunas_originais']
    extra = [repr(c) for c in orig if c not in PAD]
    falt = [c for c in PAD if c not in [str(x).strip() for x in orig]]
    diff = ('extras: ' + ', '.join(extra) if extra else '') + ('; ausentes: ' + ', '.join(falt) if falt else '')
    print(f"| {i} | {info['arquivo']} | {', '.join(info['abas'])} | {info['aba_usada']} | {', '.join(a for a, _ in info['abas_ignoradas'])} | {len(df)} | {info['linhas_vazias_ignoradas']} | {', '.join(d.strftime('%d/%m/%Y') for d in datas)} | {'Sim' if ok else 'NÃO'} | {df['Prefixo'].nunique()} | {diff or '—'} |")

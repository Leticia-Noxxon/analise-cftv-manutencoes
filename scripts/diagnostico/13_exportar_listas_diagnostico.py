"""Exporta listas auxiliares do diagnóstico (prefixos CFTV, prefixos manutenção) e checksums dos arquivos brutos."""
import os, hashlib, glob
import pandas as pd
B = os.path.join(os.path.dirname(__file__), '..', '..')
D = os.path.join(B, 'data', 'processed')
c = pd.read_pickle(os.path.join(D, '_cftv_kinds.pkl'))
m = pd.read_pickle(os.path.join(D, '_manut_parsed.pkl'))
c['Empresa_pad'] = c.Empresa.str.strip()
g = c.groupby('Prefixo').agg(empresas=('Empresa_pad', lambda x: ' | '.join(sorted(set(x)))),
                             dias_com_registro=('data_arquivo', 'nunique'),
                             primeiro_dia=('data_arquivo', 'min'), ultimo_dia=('data_arquivo', 'max'))
g['tem_manutencao'] = g.index.isin(set(m.Prefixo))
g.to_csv(os.path.join(D, 'diagnostico_prefixos_cftv.csv'), encoding='utf-8-sig')
mm = m.groupby('Prefixo').agg(qtd_formularios=('linha_excel', 'size'), linhas_excel=('linha_excel', lambda x: ','.join(map(str, x))),
                              datas=('Data', lambda x: ' | '.join(x)), garagens=('Garagem', lambda x: ' | '.join(sorted(set(x)))))
mm['existe_no_cftv'] = mm.index.isin(set(c.Prefixo))
mm.to_csv(os.path.join(D, 'diagnostico_prefixos_manutencao.csv'), encoding='utf-8-sig')
with open(os.path.join(D, 'CHECKSUMS_SHA256_raw.txt'), 'w') as f:
    for p in sorted(glob.glob(os.path.join(B, 'data', 'raw', '*.xlsx'))):
        f.write(hashlib.sha256(open(p, 'rb').read()).hexdigest() + '  ' + os.path.basename(p) + '\n')
print(' '.join(str(p) for p in sorted(set(m.Prefixo))))

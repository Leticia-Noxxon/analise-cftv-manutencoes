# Pasta de dados

- `raw/` — planilhas originais (Relatório CFTV - DD.MM.AAAA.xlsx e Revisão_CFTV*.xlsx). **Nunca são alteradas** pelo projeto
  e **não são versionadas no Git** (ver `.gitignore`). Para atualizar os dados, copie os novos arquivos para `data/raw/`
  (crie a pasta se não existir) e rode `python scripts/atualizar_dados.py`.
  Conferência de integridade: `data/processed/CHECKSUMS_SHA256_raw.txt`.
- `processed/` — bases tratadas geradas pelo script (CSV/XLSX): CFTV consolidado, manutenções tratadas,
  manutenção × CFTV, antes/depois, recorrências, resumo de arquivos e inconsistências.
  `cftv_consolidado.csv` (≈ 37 MB) não é versionado; a mesma base está em `cftv_consolidado.xlsx`.

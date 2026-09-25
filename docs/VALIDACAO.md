# VALIDAÇÃO MANUAL POR AMOSTRAGEM (Fase 13)

Gerado por `scripts/validacao_manual.py` em 25/09/2026 17:02 (horário de Brasília).

Amostra aleatória com semente fixa (20260925): 6 prefixos com manutenção + 4 sem manutenção, acrescida de casos especiais (recorrência, mais de um formulário no mesmo dia, prefixo ausente do CFTV, observação mais longa do arquivo) quando não sorteados.

**O que foi comparado em cada prefixo:**

1. **Planilha original** (lida de novo com openpyxl, sem usar o código do pipeline) → cor esperada de cada dia, recalculada com a regra da especificação (OFFLINE → vermelho; “error” sem OFFLINE → laranja; tudo ONLINE ok → verde; “-” e vazio ignorados; sem linha → branco).
2. **Base processada** `data/processed/cftv_consolidado.csv` → status, linha do Excel e texto original de cada câmera.
3. **JSON do site** `site/public/data/cftv.json` → cor de cada dia.
4. **Painel** (navegador headless) → cor de cada quadrado exibido; painel de detalhe de uma célula (status, SD, Login, Gravação por câmera); quantidade de bolinhas; resultado mostrado no painel de manutenção; texto integral da observação do técnico (comparado caractere a caractere com a planilha).
5. **Formulários**: quantidade na planilha × `manutencoes_tratadas.csv` × JSON.

## Resultado: 14 de 14 prefixos sem nenhuma divergência

| Prefixo | Manutenção? | Dias conferidos (planilha = processado = JSON = painel) | Registros na planilha | Formulários (planilha/processado/JSON) | Bolinhas no painel | Resultado exibido | Observações do técnico | Divergências |
|---|---|---|---|---|---|---|---|---|
| 51113 | sim | 25/25 | 16 | 1/1/1 | 1 | SEM DADOS PARA VALIDAR | 1/1 idênticas (maior: 91 caracteres) | nenhuma |
| 31105 | sim | 25/25 | 16 | 1/1/1 | 1 | NÃO RESOLVIDO | 1/1 idênticas (maior: 376 caracteres) | nenhuma |
| 61314 | sim | 25/25 | 16 | 1/1/1 | 1 | RESOLVIDO | 1/1 idênticas (maior: 102 caracteres) | nenhuma |
| 31012 | sim | 25/25 | 16 | 1/1/1 | 1 | NÃO RESOLVIDO | 1/1 idênticas (maior: 45 caracteres) | nenhuma |
| 52774 | sim | 25/25 | 13 | 1/1/1 | 1 | SEM DADOS PARA VALIDAR | 1/1 idênticas (maior: 123 caracteres) | nenhuma |
| 73219 | sim | 25/25 | 16 | 1/1/1 | 1 | SEM DADOS PARA VALIDAR | 1/1 idênticas (maior: 220 caracteres) | nenhuma |
| 86148 | não | 25/25 | 16 | 0/0/0 | 0 | — | — | nenhuma |
| 31521 | não | 25/25 | 16 | 0/0/0 | 0 | — | — | nenhuma |
| 73958 | não | 25/25 | 16 | 0/0/0 | 0 | — | — | nenhuma |
| 68413 | não | 25/25 | 16 | 0/0/0 | 0 | — | — | nenhuma |
| 31005 | sim | 25/25 | 16 | 1/1/1 | 1 | RESOLVIDO COM RECORRÊNCIA | 1/1 idênticas (maior: 189 caracteres) | nenhuma |
| 32062 | sim | 25/25 | 16 | 2/2/2 | 1 | RESOLVIDO COM RECORRÊNCIA | 2/2 idênticas (maior: 107 caracteres) | nenhuma |
| 11435 | sim | 25/25 | 0 | 1/1/1 | 1 | SEM DADOS PARA VALIDAR | 0/0 idênticas (maior: 0 caracteres) | nenhuma |
| 31094 | sim | 25/25 | 16 | 1/1/1 | 1 | NÃO RESOLVIDO | 1/1 idênticas (maior: 587 caracteres) | nenhuma |

## Detalhes

- **51113** — cores (01/09→25/09, V=verde L=laranja R=vermelho espaço=sem dados): `VVVV   VVVV   VVVV  VVVV `; célula conferida no painel: 2026-09-01.
- **31105** — cores (01/09→25/09, V=verde L=laranja R=vermelho espaço=sem dados): `RRRR   RRRR   RRRR  RRRR `; célula conferida no painel: 2026-09-01.
- **61314** — cores (01/09→25/09, V=verde L=laranja R=vermelho espaço=sem dados): `RRRR   RRRR   RVVV  VVVV `; célula conferida no painel: 2026-09-01.
- **31012** — cores (01/09→25/09, V=verde L=laranja R=vermelho espaço=sem dados): `VVVV   VVLR   RRRR  RRRR `; célula conferida no painel: 2026-09-10.
- **52774** — cores (01/09→25/09, V=verde L=laranja R=vermelho espaço=sem dados): `VVVV   VVVV   VVVV  V    `; célula conferida no painel: 2026-09-01.
- **73219** — cores (01/09→25/09, V=verde L=laranja R=vermelho espaço=sem dados): `VVVV   VVVV   VVVV  VVVV `; célula conferida no painel: 2026-09-01.
- **86148** — cores (01/09→25/09, V=verde L=laranja R=vermelho espaço=sem dados): `VVVV   VVVV   VVVV  VVVV `; célula conferida no painel: 2026-09-01.
- **31521** — cores (01/09→25/09, V=verde L=laranja R=vermelho espaço=sem dados): `VRRR   RRRR   RRRR  RRRR `; célula conferida no painel: 2026-09-02.
- **73958** — cores (01/09→25/09, V=verde L=laranja R=vermelho espaço=sem dados): `VVVV   RRVV   VVVV  VVVV `; célula conferida no painel: 2026-09-08.
- **68413** — cores (01/09→25/09, V=verde L=laranja R=vermelho espaço=sem dados): `RRRR   RRRR   RRRR  RRRR `; célula conferida no painel: 2026-09-01.
- **31005** — cores (01/09→25/09, V=verde L=laranja R=vermelho espaço=sem dados): `RLLL   LLLV   VVVV  VRRV `; célula conferida no painel: 2026-09-01.
- **32062** — cores (01/09→25/09, V=verde L=laranja R=vermelho espaço=sem dados): `VVVV   VVVR   VVVV  VRRR `; célula conferida no painel: 2026-09-11.
- **11435** — cores (01/09→25/09, V=verde L=laranja R=vermelho espaço=sem dados): `                         `; célula conferida no painel: —.
- **31094** — cores (01/09→25/09, V=verde L=laranja R=vermelho espaço=sem dados): `RRRR   RRRR   RRRR  RRRR `; célula conferida no painel: 2026-09-01.

## Conclusão

Os dados exibidos no painel correspondem às planilhas originais em todos os pontos conferidos acima. Observações longas aparecem completas (sem corte) no painel de manutenção.

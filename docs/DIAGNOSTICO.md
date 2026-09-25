# DIAGNÓSTICO DOS DADOS — Análise CFTV + Manutenções
Gerado em 25/09/2026 (horário de Brasília) — Fases 1 a 4 da especificação (§32 e §48).
Nenhum dashboard foi construído ainda. Nenhum arquivo original foi alterado.

Scripts que produziram estes números: `scripts/01_…` a `scripts/13_…` (Python/pandas/openpyxl, venv `/workspace/venv`).
Saídas auxiliares integrais: `docs/_inspecao_estrutura.txt`, `docs/_inspecao_manutencao.txt`, `docs/_manutencao_registros_completos.txt` (todas as 324 respostas, texto completo, sem truncar), `docs/_indicios_mapeamento.txt`, `docs/_texto_livre_manutencao.txt`, `data/processed/diagnostico_prefixos_cftv.csv`, `data/processed/diagnostico_prefixos_manutencao.csv`, `data/processed/CHECKSUMS_SHA256_raw.txt`.

---

## 1. Arquivos de origem

Pasta de origem (computador da Letícia): `C:\Users\letic\Downloads\analise 200 câmeras 25092026\`
Cópia fiel (bytes idênticos, tamanhos conferidos, SHA-256 registrado) em `data/raw/`.

| Tipo | Qtd | Observação |
|---|---|---|
| "Relatório CFTV - DD.MM.2026.xlsx" | **16** | 01, 02, 03, 04, 08, 09, 10, 11, 15, 16, 17, 18, 21, 22, 23, 24/09/2026 |
| "Revisão_CFTV2026-09-25_13_34_23.xlsx" | 1 | respostas do formulário de manutenção |
| "Análise 200 câmeras - Consolidado.xlsx" | — | **IGNORADO**: é saída de uma tarefa anterior, não é fonte |

**Datas SEM arquivo CFTV dentro do período 01–24/09:** 05/09 (sáb), 06/09 (dom), 07/09 (seg – feriado), 12/09 (sáb), 13/09 (dom), **14/09 (seg)**, 19/09 (sáb), 20/09 (dom). Essas colunas ficarão BRANCAS (sem dados) para todos os prefixos.

## 2. Relatórios CFTV — abas, aba escolhida, registros, datas

Todos os 16 arquivos têm exatamente **2 abas**:
- `Tabela` → **IGNORADA**: contém 1 tabela dinâmica ("Contagem de Prefixo" por Empresa × Status, com filtros Data/Manutenção). É resumo, não é base de registros. Conferência: o "Total Geral" da tabela dinâmica é igual ao nº de registros da aba de detalhe em **todos** os 16 arquivos (script 12) — confirma que a aba de detalhe é a base completa.
- `Relatório CFTV - DD.MM.2026` → **UTILIZADA**: cabeçalho na linha 1 (Prefixo + Câmera 21…26), uma linha por veículo. Identificada automaticamente (`scripts/cftv_loader.py`: aba sem tabela dinâmica e com cabeçalho Prefixo + "Câmera NN").

| # | Arquivo | Abas existentes | Aba utilizada | Aba ignorada | Registros | Linhas vazias ao final | Data (coluna) | Data = nome? | Prefixos únicos | Colunas diferentes do padrão |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Relatório CFTV - 01.09.2026.xlsx | Tabela, Relatório CFTV - 01.09.2026 | Relatório CFTV - 01.09.2026 | Tabela | 5120 | 433 | 01/09/2026 | Sim | 5120 | extras: 'Última Transmissão' |
| 2 | Relatório CFTV - 02.09.2026.xlsx | Tabela, Relatório CFTV - 02.09.2026 | Relatório CFTV - 02.09.2026 | Tabela | 5150 | 377 | 02/09/2026 | Sim | 5150 | — |
| 3 | Relatório CFTV - 03.09.2026.xlsx | Tabela, Relatório CFTV - 03.09.2026 | Relatório CFTV - 03.09.2026 | Tabela | 5164 | 354 | 03/09/2026 | Sim | 5164 | — |
| 4 | Relatório CFTV - 04.09.2026.xlsx | Tabela, Relatório CFTV - 04.09.2026 | Relatório CFTV - 04.09.2026 | Tabela | 4526 | 263 | 04/09/2026 | Sim | 4526 | ; ausentes: Manutenção |
| 5 | Relatório CFTV - 08.09.2026.xlsx | Tabela, Relatório CFTV - 08.09.2026 | Relatório CFTV - 08.09.2026 | Tabela | 5072 | 422 | 08/09/2026 | Sim | 5072 | — |
| 6 | Relatório CFTV - 09.09.2026.xlsx | Tabela, Relatório CFTV - 09.09.2026 | Relatório CFTV - 09.09.2026 | Tabela | 5124 | 390 | 09/09/2026 | Sim | 5124 | — |
| 7 | Relatório CFTV - 10.09.2026.xlsx | Tabela, Relatório CFTV - 10.09.2026 | Relatório CFTV - 10.09.2026 | Tabela | 5133 | 380 | 10/09/2026 | Sim | 5133 | — |
| 8 | Relatório CFTV - 11.09.2026.xlsx | Tabela, Relatório CFTV - 11.09.2026 | Relatório CFTV - 11.09.2026 | Tabela | 5151 | 376 | 11/09/2026 | Sim | 5151 | — |
| 9 | Relatório CFTV - 15.09.2026.xlsx | Tabela, Relatório CFTV - 15.09.2026 | Relatório CFTV - 15.09.2026 | Tabela | 5162 | 351 | 15/09/2026 | Sim | 5162 | — |
| 10 | Relatório CFTV - 16.09.2026.xlsx | Tabela, Relatório CFTV - 16.09.2026 | Relatório CFTV - 16.09.2026 | Tabela | 5188 | 343 | 16/09/2026 | Sim | 5188 | — |
| 11 | Relatório CFTV - 17.09.2026.xlsx | Tabela, Relatório CFTV - 17.09.2026 | Relatório CFTV - 17.09.2026 | Tabela | 5184 | 365 | 17/09/2026 | Sim | 5184 | — |
| 12 | Relatório CFTV - 18.09.2026.xlsx | Tabela, Relatório CFTV - 18.09.2026 | Relatório CFTV - 18.09.2026 | Tabela | 5184 | 339 | 18/09/2026 | Sim | 5184 | extras: 'Câmera 21 ' |
| 13 | Relatório CFTV - 21.09.2026.xlsx | Tabela, Relatório CFTV - 21.09.2026 | Relatório CFTV - 21.09.2026 | Tabela | 5233 | 375 | 21/09/2026 | Sim | 5233 | — |
| 14 | Relatório CFTV - 22.09.2026.xlsx | Tabela, Relatório CFTV - 22.09.2026 | Relatório CFTV - 22.09.2026 | Tabela | 5228 | 349 | 22/09/2026 | Sim | 5228 | — |
| 15 | Relatório CFTV - 23.09.2026.xlsx | Tabela, Relatório CFTV - 23.09.2026 | Relatório CFTV - 23.09.2026 | Tabela | 5240 | 351 | 23/09/2026 | Sim | 5240 | — |
| 16 | Relatório CFTV - 24.09.2026.xlsx | Tabela, Relatório CFTV - 24.09.2026 | Relatório CFTV - 24.09.2026 | Tabela | 5250 | 348 | 24/09/2026 | Sim | 5250 | — |

Notas da tabela:
- "Linhas vazias ao final" = linhas totalmente vazias (apenas formatação) após o último registro; não há linhas vazias intercaladas. Foram desconsideradas (não contêm dado).
- A coluna **Data** tem um único valor por arquivo e **coincide com a data do nome do arquivo em 16/16**.
- **Total de registros CFTV: 82.109** (veículo × dia).

## 3. Prefixos

- **Prefixos únicos no CFTV: 5.429** (e não ~200). Cada arquivo diário tem de 4.526 a 5.250 veículos, de 17 empresas. Faixa de prefixos: 10001 a 86630.
- A especificação fala em "aproximadamente 200 câmeras/veículos". O grupo que mais se aproxima disso é o de **veículos que receberam manutenção: 306 prefixos** (324 formulários). → ver QUESTÃO EM ABERTO Q1 (escopo da matriz).
- Presença ao longo dos 16 dias: 4.102 prefixos aparecem nos 16 dias; 765 em 15; os demais em menos dias (30 aparecem em apenas 1 dia). Lista completa: `data/processed/diagnostico_prefixos_cftv.csv`.
- **Duplicidades prefixo + data no CFTV: 0** (nenhum prefixo repetido dentro de um mesmo arquivo; cada arquivo = uma data).
- **50 prefixos mudam de empresa** durante o mês (ex.: 31361–31375 METROPOLE - AE CARVALHO ↔ METROPOLE - EXPANDIR; 31425, 31489… METROPOLE - EXPANDIR ↔ METROPOLE - IGUATEMI).

### Empresas (coluna Empresa do CFTV) — 17 valores, registros no período
NORTE BUSS A1 10.154 · VIA SUDESTE 9.929 · SANTA BRIGIDA 9.730 · A2 TRANSPORTES 6.993 · VIACAO GRAJAU 6.384 · NORTE BUSS A2 4.959 · METROPOLE - ITAIM 4.765 · GATO PRETO 4.174 · METROPOLE - IMPERADOR 3.615 · METROPOLE PAULISTA - DEPINEDO 3.545 · METROPOLE - AE CARVALHO 3.522 · METROPOLE - MBOI - MIRIM 2.879 · ALFA RODOBUS 2.808 · METROPOLE - IGUATEMI 2.682 · ALFA RODOBUS SPE 2.424 · METROPOLE - EXPANDIR 2.046 · GATO PRETO A1 1.500.

- 5 nomes vêm com **espaço no final** ('GATO PRETO ', 'METROPOLE - AE CARVALHO ', 'METROPOLE - ITAIM ', 'METROPOLE PAULISTA - DEPINEDO ', 'VIA SUDESTE ') → padronização: remover espaços nas pontas.
- **SANTA BRIGIDA não aparece no arquivo de 04/09** (0 registros; ~650 nos outros dias). O arquivo de 04/09 também não tem a coluna Manutenção e foi salvo em 08/09. Santa Brígida é a 3ª garagem com mais manutenções (59).

## 4. Colunas encontradas × colunas padronizadas

| Coluna original | Arquivos | Coluna padronizada | Observação |
|---|---|---|---|
| Prefixo | 16/16 | prefixo (inteiro) | sempre numérico, nunca vazio |
| Data | 16/16 | data | datetime; = data do nome do arquivo |
| Empresa | 16/16 | empresa | remover espaços nas pontas |
| Câmera 21 / **'Câmera 21 '** (18/09, espaço no final) | 16/16 | camera_21 | cabeçalho normalizado (trim + espaços múltiplos) |
| Câmera 22 … Câmera 26 | 16/16 | camera_22 … camera_26 | |
| Status | 16/16 | status_operacional_cftv | classificação manual/operacional do veículo (ver §6) — NÃO é o texto da câmera |
| Manutenção | 15/16 (ausente em 04/09) | ultima_manutencao_cftv | data da última manutenção ou '#N/A' (ver §7) |
| Última Transmissão | 1/16 (só 01/09) | ultima_transmissao | texto "01/09/2026, 10:15:09"; horários ≈ 10h |
| (derivada) | — | arquivo_origem, linha_excel | rastreabilidade até o Excel |

**Não existem colunas FRONTAL / FRENTE / CORREDOR nos arquivos CFTV** — as câmeras são identificadas somente por número de canal (21 a 26). Também não existe "Corredor" sem número em nenhum arquivo (nem no formulário).

### Grade de colunas por empresa (coluna em branco ≠ '-')
- Empresas com grade de **2 colunas** (23–26 sempre vazias): A2 TRANSPORTES, ALFA RODOBUS SPE, NORTE BUSS A1, NORTE BUSS A2.
- Grade de **3 colunas** (24–26 vazias): METROPOLE - AE CARVALHO, ALFA RODOBUS (em 24/09 a ALFA RODOBUS passou a ter só 2 colunas).
- Grade de **6 colunas**: demais empresas.

## 5. Valores das células de câmera (todas as 6 colunas × 82.109 linhas = 492.654 células)

| Valor | Qtd | Interpretação pela especificação |
|---|---|---|
| `ONLINE (SD: ok, Login: ok, Gravação: ok)` | 215.730 | ONLINE NORMAL (verde) |
| (célula vazia – coluna fora da grade da empresa) | 117.284 | não existe câmera nessa coluna para esse arquivo/empresa |
| `-` | 110.100 | **a definir (Q2)** |
| `OFFLINE` | 31.808 | OFFLINE (vermelho) |
| `ONLINE (SD: error, Login: ok, Gravação: error)` | 17.732 | ONLINE COM ERRO (laranja) – erros: SD, Gravação |

- Só existem **esses 4 textos** distintos. Nunca aparece "Login: error"; o único padrão de erro é SD + Gravação simultâneos.
- Nenhuma linha fica sem pelo menos uma câmera com valor real (ONLINE/OFFLINE).
- Status geral preliminar pela regra da especificação (§6), desconsiderando '-': VERDE 54.037 · VERMELHO 16.374 · LARANJA 11.698 registros.

### O que significa '-' (investigação)
- É **estável por prefixo/câmera**: de 24.674 pares prefixo×coluna preenchidos, 7.102 são **sempre '-'** nos 16 dias, 17.572 têm valor real e só 295 alternam entre '-' e valor real.
- Ex.: 1.968 prefixos em empresas de grade de 6 colunas têm 24, 25 e 26 **sempre '-'**; isso bate com o formulário: veículos "Padron" têm câmeras reais só em 21–23 (134/135) e "Articulado" em 21–26 (165/176).
- A coluna **Status** do próprio CFTV dá **"OK" em 31.857 linhas que contêm '-'** → a operação não trata '-' como falha.
- Quando a operação marca "Câmera Inexistente", as câmeras aparecem como **OFFLINE**, não como '-'.
- Quase todas as alternâncias '-' ↔ valor vêm de uma **anomalia da ALFA RODOBUS em 03/09**: os valores das colunas 21 e 22 aparecem trocados para ~150 veículos (21='-' e 22=ONLINE, quando em todos os outros dias é 21=ONLINE, 22='-'). Em 24/09 a coluna 23 da ALFA RODOBUS ficou vazia em vez de '-'.
- **Conclusão provável:** '-' = canal sem câmera cadastrada/instalada nessa posição (sem informação), e não OFFLINE nem erro. **Não decidido — ver Q2.**

## 6. Coluna Status (classificação operacional do CFTV)
Valores (registros): OK 54.034 · Erro no SD 10.392 · 1 ou + cam Off 7.584 · 100% Offline 3.808 · Em espera por câmera/material 2.161 · Câmera Travada 1.776 · Câmera Inexistente 1.182 · Manutenção/Sem Transmissão 697 · Infiltração 275 · Substituição de câmera 113* · Vandalismo 63 · Substituição de TDM 12* · Substituição de UCP 12* (*só em 01/09).
- Todo Status "OK" tem todas as câmeras reais ONLINE ok (100%); só 3 linhas com todas ok têm outro Status (Infiltração 1, Substituição de câmera 2).
- "100% Offline" ⇔ todas as câmeras reais OFFLINE (100%).
- Os demais são rótulos manuais (motivo) que se sobrepõem aos textos das câmeras. Ex.: "Câmera Inexistente" aparece com câmeras OFFLINE → pela regra da especificação a célula fica VERMELHA (ver Q9).
- A especificação manda calcular a cor pelo texto das câmeras; o Status será mantido como informação complementar.

## 7. Coluna "Manutenção" do CFTV
- Contém **data** (46.835 células; de 19/01/2026 a 23/09/2026) ou o texto **'#N/A'** (30.748 — resultado de PROCV sem correspondência). Ausente no arquivo de 04/09 (4.526).
- Nunca é posterior à data do arquivo → é a **"data da última manutenção registrada"** do veículo, atualizada ao longo dos dias (403 prefixos mudam de valor no mês).
- Comparação com o formulário: das 324 manutenções do formulário, **218 aparecem no CFTV com a data do DIA ANTERIOR** e 55 com a mesma data. As de D-1 são justamente as preenchidas entre **00:00 e 05:59** (turno da noite): a operação registra a manutenção na data do início do turno. Manutenções das 22h–23h aparecem com a mesma data. → ver Q4.

## 8. Arquivo de manutenção — Revisão_CFTV2026-09-25_13_34_23.xlsx

### Abas
- `Sheet1` (A1:V325) → **base dos registros**: 1 linha de cabeçalho + **324 respostas**, 22 colunas, sem linhas vazias, sem fórmulas, sem células mescladas.
- `Planilha1` (B1:G325) → **auxiliar, será ignorada**: coluna B é cópia da coluna Garagem (324 valores) e F/G é uma lista das 11 garagens com fórmulas `=COUNTIF(B:B,F2)` (contagem por garagem). Não contém informação nova.

### Colunas (Sheet1), preenchimento e conteúdo
| Coluna | Preench. | % | Distintos | Conteúdo |
|---|---|---|---|---|
| Prefixo | 324 | 100% | 306 | número inteiro do veículo (coluna própria, não é texto livre) |
| Nome | 324 | 100% | 14 | técnico |
| Data | 324 | 100% | 313 | **texto** em português: "sexta-feira, setembro 25, 2026 09:40" (dia-da-semana, mês DD, AAAA HH:MM). 100% interpretável; dia da semana confere em 324/324 |
| ID | 324 | 100% | 255 | número (provável ID do equipamento/UCP do veículo); **32500 repetido 54×** (52 de FELIX SECURITY GABRIEL + 2 de Jonathan Gonçalves) → valor genérico; 4 IDs usados por mais de um prefixo; 4 prefixos com 2 IDs |
| Garagem | 324 | 100% | 11 | garagem (nome diferente do campo Empresa do CFTV) |
| Tecnologia | 324 | 100% | 5 | tipo de veículo: Articulado 176, Padron 135, Midi 11, Mini 1, Básico 1 |
| Câmera Utilizada | 16 | 5% | 3 | quantidade de câmeras novas usadas (0/1/2) |
| Problemas Detectados: Câm. Frontal | 172 | 53% | 45 | múltipla escolha, itens separados por quebra de linha |
| Ações: Câm. Frontal | 170 | 52% | 40 | idem |
| Problemas Detectados: Câm. Frente | 209 | 65% | 34 | |
| Ações: Câm. Frente | 207 | 64% | 32 | |
| Problemas Detectados: Câm. Corredor 1 | 147 | 45% | 26 | |
| Problemas Detectados: Câm. Corredor 2 | 73 | 23% | 16 | |
| Ações: Câm. Corredor 2 | 72 | 22% | 19 | |
| Switch Utilizado | 19 | 6% | 2 | quantidade de switches usados (0/1) |
| Problemas Detectados: Câm. Corredor 3 | 72 | 22% | 19 | |
| Cartão de Memória Utilizado | 56 | 17% | 6 | quantidade de cartões usados (0,1,2,3,4,6) |
| Ações: Câm. Corredor 1 | 146 | 45% | 24 | (fora de ordem no arquivo — coluna R) |
| Ações: Câm. Corredor 3 | 71 | 22% | 20 | |
| Problemas Detectados: Câm. Corredor 4 | 69 | 21% | 23 | |
| Ações: Câm. Corredor 4 | 68 | 21% | 24 | |
| Observações | 255 | 79% | 225 | texto livre, até 587 caracteres, 141 com quebras de linha |

Os campos "Utilizada" são texto ('0','1',…). 88 formulários não têm nenhuma coluna de posição preenchida (só Observações).

**Problemas (opções do formulário):** Nenhuma anomalia identificada; Sem gravação de imagens; Configuração incorreta da câmera; Câmera mal reposicionada; Câmera inoperante; Câmera travada; Cabeamento rompido/danificado; RJ45 crimpado incorretamente; Câmera com infiltração; Câmera sem cartão de memória; Switch apresentando falha; Câmera desligada manualmente; Falha na conexão dos cabos; Câmera removida por terceiros; Câmera com sinal de vandalismo; Conexões do switch incorretas; Câmera não fixada corretamente; Switch não fixado corretamente; Fusível queimado.

**Ações (opções):** Nenhuma ação realizada; Normalização da gravação de imagens; Correção e ajuste da configuração da câmera; Reposicionamento adequado da câmera; Reinicialização da câmera; Inserção ou substituição do cartão de memória; Ativação da câmera; Crimpagem correta do conector RJ45; Substituição do switch; Substituição da câmera defeituosa; Substituição do cabeamento; Fixação adequada da câmera; Correção na conexão dos cabos; Reparo do cabeamento; Correção das conexões do switch; Correção da falha no switch; Instalação da câmera removida; Substituição do fusível; Câmera encaminhada para manutenção; Fixação adequada do switch.

### Texto livre (Observações) — achados
- **143 formulários citam câmeras por número** ("Camera 21", "câmera 22", "Câmeras 22 e 23", "Câmara 23"…).
- **52 formulários (FELIX SECURITY GABRIEL, Via Sudeste) usam notação "C1…C6"** (ex.: "C1/C4 FORMATAÇÃO DE CARTÃO… C2/C6 CÂMERA EM CURTO… 100% ONLINE") — não se sabe se C1 = Câmera 21.
- ~43 citam pen drive/UCP (ex.: 23× "Foi feito a substituição do pen drive pelo cartão de memória").
- **Nº de série / MAC** em 4 formulários: linha 2 (73381), 156 (73357), 193 (73203) com série e MAC instalados/retirados; linha 296 (31986) só MAC retirado/instalado. Na linha 193 o texto do nº de série está quebrado em linhas ("210235UDL5\nF247004359").
- **Possíveis pendências** (não há coluna de pendência): 12 textos, ex.: linha 91 (52133) "PENDENTE — Necessário trocar SD câmera 26"; linha 117 (11755) "aguardando chegar câmera para substituição"; linha 57 (52752) "Não foi possível trocar a câmera 22…"; linha 59 (61350) "falta colocar um cartão sd"; linha 71, 167, 203, 264, 307, 320… Além disso, a ação "Câmera encaminhada para manutenção" aparece 2×.
- **Prefixo divergente no texto:** linha 191 (Prefixo=52074, texto começa com "52023"); linha 196 (Prefixo=52042, texto diz "PREFIXO INCORRETO: 52704"); linha 236 (ID=34182, texto "68582 - 34142").

### Datas e horários das manutenções
- De **11/09/2026 03:08** a **25/09/2026 09:40**.
- Por dia (formulários): 11/09 10 · 12/09 3 · 14/09 17 · 15/09 33 · 16/09 66 · 17/09 49 · 18/09 18 · 19/09 23 · 20/09 1 · 21/09 18 · 22/09 15 · 23/09 21 · 24/09 37 · **25/09 13**.
- **13 manutenções em 25/09** (fora do período CFTV 01–24/09; não existe CFTV de 25/09).
- **44 manutenções em dias sem arquivo CFTV** (12/09, 14/09, 19/09, 20/09) → célula branca + bolinha azul.
- Horários: 262 de 324 entre 22:00 e 05:59 (turno da noite); o CFTV parece ser gerado por volta das 10h (única referência: Última Transmissão de 01/09).

### Prefixos, duplicidades, técnicos, garagens
- **324 formulários, 306 prefixos distintos.** 305 existem no CFTV.
- **Prefixo da manutenção que NÃO existe no CFTV: 11435** (linha 111; Santa Brigida; Leandro Resende; 19/09 03:25; Padron; sem observações).
- **18 prefixos com 2 formulários**; em **11 deles os 2 formulários são do mesmo dia** (22 linhas): 32062, 51060, 51573, 52074, 52110, 52711, 52752, 52919, 52936, 68594, 31654. Nenhuma linha é totalmente idêntica a outra (ex.: 52110 tem 2 formulários com 1 minuto de diferença e o mesmo texto).
- Das 324 manutenções: 259 têm registro CFTV no próprio dia; 317 têm registro anterior; **55 não têm nenhum registro CFTV posterior** (24/09, 25/09 etc. → SEM DADOS PARA VALIDAR).
- **Técnicos (14 nomes):** Leandro Resende 59 · FELIX SECURITY GABRIEL 52 · Anderson Silva 48 · Luiz Rodrigo 44 · Joel 26 · Jonathan Gonçalves 25 · Rafael Diniz 15 · Gesnei souza 14 · Rafael Menezes Rocha 12 · Gustavo Nunes 10 · John Lima 9 · Abner melo 8 · **Abner Melo 1** (mesma pessoa, diferença de maiúscula) · **Lui 1** (linha 144, Iguatemi — provável "Luiz Rodrigo", não confirmado).
- **Garagens (11):** Via Sudeste Sapopemba 100 · Viação Metrópole Iguatemi 60 · Santa Brigida 59 · Viação Metrópole Imperador 26 · Viação Grajaú 25 · Viação Metrópole Itaim 14 · A2 Transportes 12 · Viação Metrópole M'Boi Mirim 9 · Viação Metrópole Pinedo 9 · Viação Metrópole AE Carvalho 8 · Via Sudeste Cursino 2.
- Garagem × Empresa CFTV (pelo prefixo): correspondência 1-para-1 sem conflito — Via Sudeste Sapopemba/Cursino → VIA SUDESTE; Viação Metrópole Pinedo → METROPOLE PAULISTA - DEPINEDO; Viação Metrópole M'Boi Mirim → METROPOLE - MBOI - MIRIM; Viação Grajaú → VIACAO GRAJAU; demais óbvias.

## 9. Câmera 21–26 × posição (FRONTAL / FRENTE / CORREDOR 1–4)
- **Nenhum arquivo traz um mapeamento explícito.** O CFTV só tem números; o formulário só tem posições nas colunas estruturadas e números no texto livre.
- **Indício forte (inferido, NÃO aplicado):** cruzando os formulários em que o técnico cita UMA câmera no texto e marca problema em UMA única posição (38 casos), e os casos com a mesma quantidade de câmeras citadas e posições com problema (124 pares), a correspondência é sempre a mesma, **sem nenhuma contradição**:
  - Câmera 21 = FRONTAL · Câmera 22 = FRENTE · Câmera 23 = CORREDOR 1 · Câmera 24 = CORREDOR 2 · Câmera 25 = CORREDOR 3 · Câmera 26 = CORREDOR 4
  - vale para Articulado, Padron (21–23), Midi e Básico. Detalhes: `docs/_indicios_mapeamento.txt`.
- Por §14 da especificação isso **não foi adotado**; depende de confirmação (Q3).

## 10. Campos inesperados
- CFTV: "Última Transmissão" (só 01/09); "Status" (classificação operacional com 13 valores); "Manutenção" (data da última manutenção / #N/A).
- Formulário: "ID", "Tecnologia", "Câmera Utilizada", "Switch Utilizado", "Cartão de Memória Utilizado"; aba "Planilha1" com fórmulas COUNTIF.
- Notação "C1…C6" em observações.

## 11. Inconsistências encontradas
1. Cabeçalho 'Câmera 21 ' com espaço (18/09) → normalizado.
2. Empresa com espaços no final (5 nomes) → normalizado.
3. Arquivo 04/09 sem a coluna Manutenção e **sem a empresa SANTA BRIGIDA inteira**.
4. Arquivo 01/09 tem coluna extra "Última Transmissão" e 3 Status que não aparecem em outros dias (Substituição de câmera/TDM/UCP).
5. ALFA RODOBUS em 03/09: valores das colunas 21/22 trocados (~150 veículos). Em 24/09 a coluna 23 vazia em vez de '-'. (Nenhum veículo ALFA teve manutenção.)
6. 50 prefixos mudam de empresa no mês.
7. Status "Câmera Inexistente" aparece com câmeras OFFLINE (seriam VERMELHAS pela regra da especificação).
8. Formulário: ID genérico 32500 (54×); prefixo divergente no texto (linhas 191 e 196); ID divergente no texto (linha 236); nome "Abner melo/Abner Melo"; "Lui".
9. Formulário: prefixo 11435 inexistente no CFTV.
10. Manutenções da madrugada aparecem no CFTV com data D-1.
11. Série quebrada em duas linhas (linha 193) e com prefixos estranhos ("H;A0", "HB20").

## 12. Prefixos com manutenção (306)
11038 11044 11052 11053 11055 11061 11064 11067 11068 11072 11078 11086 11088 11097 11100 11101 11103 11109 11111 11435 11452 11457 11471 11536 11661 11669 11677 11682 11689 11691 11694 11695 11714 11725 11738 11744 11754 11755 11759 11764 11775 11786 11796 11801 11807 11810 11819 11829 11831 11834 11840 11857 11873 11874 11880 11883 11884 11903 31003 31005 31011 31012 31014 31093 31094 31095 31100 31105 31120 31136 31157 31165 31180 31182 31204 31205 31210 31212 31245 31255 31260 31262 31269 31299 31484 31486 31503 31560 31590 31593 31615 31622 31624 31629 31635 31651 31652 31654 31656 31657 31661 31664 31667 31668 31670 31673 31700 31733 31738 31750 31751 31753 31755 31758 31760 31761 31762 31763 31771 31775 31786 31787 31795 31816 31818 31822 31823 31841 31844 31859 31862 31927 31948 31949 31950 31951 31952 31953 31955 31956 31960 31962 31964 31972 31973 31980 31983 31984 31986 32038 32039 32062 32091 32100 32129 32198 32272 32521 32616 32641 32960 51003 51004 51022 51057 51060 51061 51079 51111 51113 51116 51117 51121 51122 51132 51133 51143 51218 51573 51574 51578 51579 52014 52021 52024 52041 52042 52055 52059 52070 52074 52078 52103 52104 52105 52110 52111 52113 52115 52119 52124 52126 52127 52132 52133 52139 52145 52148 52711 52712 52714 52718 52734 52744 52745 52748 52749 52752 52754 52762 52763 52767 52774 52775 52782 52788 52796 52799 52828 52834 52835 52838 52843 52868 52901 52903 52904 52905 52906 52907 52909 52910 52911 52913 52919 52922 52923 52924 52932 52935 52936 52943 61065 61070 61213 61224 61228 61273 61282 61284 61295 61311 61314 61316 61327 61334 61350 61414 61454 61511 61571 61587 61589 61651 61654 61766 61793 68043 68465 68508 68582 68589 68594 68603 68639 68640 68652 68657 73004 73203 73219 73357 73362 73381 73612 73614 73642 73767 73775 73776 73785 73796 73803 73840 73864 73932

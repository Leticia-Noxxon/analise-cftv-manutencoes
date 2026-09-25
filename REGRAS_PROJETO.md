# REGRAS DO PROJETO — Análise CFTV + Manutenções

> **ANTES DE QUALQUER ALTERAÇÃO NO PROJETO: LER ESTE ARQUIVO INTEIRO** e também `docs/ESPECIFICACAO_ORIGINAL.md` (fonte oficial).
> Nenhuma regra aqui pode ser alterada silenciosamente. Toda nova regra/alteração estrutural deve ser registrada no **Histórico de decisões** (final do arquivo).

Versão 1 — 25/09/2026 (Fases 1–4: leitura, estrutura, diagnóstico, regras). Dashboard ainda NÃO construído.
Diagnóstico detalhado: `docs/DIAGNOSTICO.md`.

---

## 0. Regra nº 1 (§6 da especificação — "leia e documente antes de programar")
1. Ler a especificação inteira e este arquivo antes de criar/alterar/corrigir qualquer coisa.
2. Analisar os arquivos reais antes de definir regra adicional.
3. Não alterar regra estabelecida silenciosamente.
4. Não inventar informação ausente.
5. Não eliminar dados de origem.
6. Não simplificar a lógica sem autorização.
7. Registrar toda nova regra ou alteração estrutural aqui.

## 1. Objetivo
Dashboard web interativo para investigar, por veículo (prefixo) e por dia, o estado das câmeras de CFTV e o efeito das manutenções: **ANTES → MANUTENÇÃO → DEPOIS → RECORRÊNCIA**. Para qualquer prefixo deve responder: como estava antes; qual câmera tinha problema; OFFLINE ou ONLINE com erro; qual erro; há quanto tempo; quando houve manutenção; quem fez; anomalia; o que foi feito; câmera/equipamento substituído; nº de série/MAC; pendência; como ficou no 1º registro depois; se continuou normal e por quantos dias/registros; se o problema voltou, quando, se na mesma câmera ou em outra; classificação baseada nos dados. Tudo rastreável até o arquivo/linha original. É ferramenta de investigação, não gráfico decorativo.

## 2. Arquivos utilizados
Origem: `C:\Users\letic\Downloads\analise 200 câmeras 25092026\` (computador da Letícia). Cópia intocada em `data/raw/` (SHA-256 em `data/processed/CHECKSUMS_SHA256_raw.txt`). Dados tratados em `data/processed/`. **Nunca alterar `data/raw/`.**

| Arquivo | Aba utilizada | Abas ignoradas | Motivo |
|---|---|---|---|
| Relatório CFTV - 01.09.2026.xlsx | Relatório CFTV - 01.09.2026 | Tabela | Tabela dinâmica (resumo Empresa × Status); total confere com a aba de detalhe |
| Relatório CFTV - 02.09.2026.xlsx | Relatório CFTV - 02.09.2026 | Tabela | idem |
| Relatório CFTV - 03.09.2026.xlsx | Relatório CFTV - 03.09.2026 | Tabela | idem |
| Relatório CFTV - 04.09.2026.xlsx | Relatório CFTV - 04.09.2026 | Tabela | idem |
| Relatório CFTV - 08.09.2026.xlsx | Relatório CFTV - 08.09.2026 | Tabela | idem |
| Relatório CFTV - 09.09.2026.xlsx | Relatório CFTV - 09.09.2026 | Tabela | idem |
| Relatório CFTV - 10.09.2026.xlsx | Relatório CFTV - 10.09.2026 | Tabela | idem |
| Relatório CFTV - 11.09.2026.xlsx | Relatório CFTV - 11.09.2026 | Tabela | idem |
| Relatório CFTV - 15.09.2026.xlsx | Relatório CFTV - 15.09.2026 | Tabela | idem |
| Relatório CFTV - 16.09.2026.xlsx | Relatório CFTV - 16.09.2026 | Tabela | idem |
| Relatório CFTV - 17.09.2026.xlsx | Relatório CFTV - 17.09.2026 | Tabela | idem |
| Relatório CFTV - 18.09.2026.xlsx | Relatório CFTV - 18.09.2026 | Tabela | idem |
| Relatório CFTV - 21.09.2026.xlsx | Relatório CFTV - 21.09.2026 | Tabela | idem |
| Relatório CFTV - 22.09.2026.xlsx | Relatório CFTV - 22.09.2026 | Tabela | idem |
| Relatório CFTV - 23.09.2026.xlsx | Relatório CFTV - 23.09.2026 | Tabela | idem |
| Relatório CFTV - 24.09.2026.xlsx | Relatório CFTV - 24.09.2026 | Tabela | idem |
| Revisão_CFTV2026-09-25_13_34_23.xlsx | Sheet1 | Planilha1 | auxiliar: cópia da coluna Garagem + contagem COUNTIF por garagem; sem informação nova |
| Análise 200 câmeras - Consolidado.xlsx | — | — | **NÃO é fonte** (saída de tarefa anterior) — ignorado |

**Regra de identificação automática da aba CFTV** (`scripts/cftv_loader.py`): listar todas as abas; ignorar abas com tabela dinâmica ou sem cabeçalho de registros; usar a aba cujo cabeçalho (linha 1) contém `Prefixo` e colunas `Câmera NN`. Novos arquivos passam pela mesma regra; se nenhuma ou mais de uma aba se qualificar, o processamento deve PARAR e avisar (não adivinhar).

Localização dos arquivos: todos os `.xlsx` cujo nome começa com "Relatório CFTV" (comparação com normalização Unicode NFC) e o arquivo `Revisão_CFTV*.xlsx` mais recente.

## 3. Estrutura encontrada e nomes das colunas

### 3.1 Relatório CFTV (aba de detalhe) — 1 linha por veículo por dia
Colunas originais: `Prefixo`, `Data`, `Empresa`, `Câmera 21` … `Câmera 26`, `Status`, `Manutenção` (ausente em 04/09), `Última Transmissão` (só em 01/09). Em 18/09 o cabeçalho é `'Câmera 21 '` (espaço no final).

| Original | Padronizada | Tratamento |
|---|---|---|
| Prefixo | prefixo | inteiro |
| Data | data | data; conferida com o nome do arquivo (16/16 iguais). Se divergir em arquivo futuro: avisar |
| Empresa | empresa | remover espaços nas pontas (texto preservado) |
| Câmera 21…26 (inclusive 'Câmera 21 ') | camera_21…camera_26 | cabeçalho: trim + espaços múltiplos → 1; valor original preservado integralmente |
| Status | status_operacional_cftv | preservado como informação complementar (não define a cor) |
| Manutenção | ultima_manutencao_cftv | data, '#N/A' ou ausente — preservado como auxiliar (não gera marcador) |
| Última Transmissão | ultima_transmissao | preservado quando existir |
| — | arquivo_origem, linha_excel | rastreabilidade obrigatória |

Células vazias nas colunas de câmera = a coluna não faz parte da grade daquela empresa naquele arquivo (não existe câmera ali). Nunca virar OFFLINE.

### 3.2 Revisão_CFTV (Sheet1) — 1 linha por formulário (324 linhas, 22 colunas)
`Prefixo`, `Nome` (técnico), `Data` (texto "sexta-feira, setembro 25, 2026 09:40"), `ID`, `Garagem`, `Tecnologia`, `Câmera Utilizada`, `Problemas Detectados: Câm. Frontal`, `Ações: Câm. Frontal`, `Problemas Detectados: Câm. Frente`, `Ações: Câm. Frente`, `Problemas Detectados: Câm. Corredor 1`, `Problemas Detectados: Câm. Corredor 2`, `Ações: Câm. Corredor 2`, `Switch Utilizado`, `Problemas Detectados: Câm. Corredor 3`, `Cartão de Memória Utilizado`, `Ações: Câm. Corredor 1`, `Ações: Câm. Corredor 3`, `Problemas Detectados: Câm. Corredor 4`, `Ações: Câm. Corredor 4`, `Observações`.
- Campos de Problemas/Ações: múltipla escolha, itens separados por quebra de linha → guardar texto original + lista de itens.
- Data: converter o texto para data/hora (mês em português); guardar também o texto original.
- Todas as colunas preenchidas ficam acessíveis no painel (§17 da especificação). Nenhum texto é truncado.
- Colunas identificadas **pelo nome**, não pela posição (a ordem das colunas no formulário é irregular).

## 4. Regras de consolidação (§3)
- Juntar somente as abas de detalhe válidas dos Relatórios CFTV numa única base (`data/processed/`), preservando todas as colunas relevantes e a origem (arquivo + linha).
- Antes de concatenar: comparar cabeçalhos, padronizar nomes (tabela 3.1), identificar duplicidades (prefixo + data) e campos equivalentes. Duplicidade prefixo+data encontrada hoje: 0. Se surgir no futuro: não descartar — ver Q5.
- **"Corredor" e "Corredor 1" são a MESMA câmera → padronizar ambos como CORREDOR 1.** Nunca criar "Corredor" e "Corredor 1" separados. (Hoje nenhum arquivo contém "Corredor" sem número; a regra fica ativa para textos/arquivos futuros, inclusive textos livres.)
- Posições possíveis: FRONTAL, FRENTE, CORREDOR 1, CORREDOR 2, CORREDOR 3, CORREDOR 4. Não assumir quantidade fixa: usar exatamente as câmeras existentes para cada veículo.
- **Nos arquivos CFTV as câmeras são identificadas por número (Câmera 21…26).** Mapeamento CONFIRMADO (Q3): 21 = FRONTAL, 22 = FRENTE, 23 = CORREDOR 1, 24 = CORREDOR 2, 25 = CORREDOR 3, 26 = CORREDOR 4. Exibição sempre com posição + número: "CORREDOR 1 (câm 23)".
- Implementação: `scripts/cftv/leitura_cftv.py` detecta automaticamente a aba de detalhe (cabeçalho com Prefixo + Câmera 2x; aborta se houver 0 ou >1 aba candidata), normaliza cabeçalhos/empresa e guarda `arquivo_origem`, `aba_origem`, `linha_excel`. Saída: `data/processed/cftv_consolidado.csv/.xlsx` (texto original + código + classificação de cada câmera).
- Nunca transformar ausência de registro em OFFLINE.

## 5. Regras de status

### 5.1 Interpretação do texto da câmera (§4, §5)
O texto é interpretado (não comparado literalmente): conectividade (ONLINE/OFFLINE) e, quando houver, SD, Login, Gravação (ok/error).
| Texto | Classificação | Cor |
|---|---|---|
| ONLINE com SD ok, Login ok, Gravação ok | ONLINE NORMAL | VERDE |
| ONLINE com pelo menos um campo "error" (SD, Login ou Gravação) | ONLINE COM ERRO — preservar quais erros (ex.: "Erros: SD, Gravação") | LARANJA |
| OFFLINE | OFFLINE | VERMELHO |
| `-` | **SEM CÂMERA (Q2):** o veículo não possui essa câmera — excluída da lista de câmeras, das contagens e da cor; aparece só na Auditoria | — |
| vazio | coluna inexistente para a grade → câmera não existe nesse registro | — |
Qualquer texto novo não previsto deve ser listado na auditoria e NÃO classificado por suposição.

### 5.2 Status geral do veículo no dia (§6)
Analisar todas as câmeras do prefixo na data. Prioridade: 1º OFFLINE, 2º ONLINE COM ERRO, 3º ONLINE NORMAL.
- ≥1 câmera OFFLINE → **VERMELHO** (mesmo que outras estejam ONLINE).
- nenhuma OFFLINE e ≥1 ONLINE COM ERRO → **LARANJA**.
- somente se TODAS ONLINE com SD ok, Login ok, Gravação ok → **VERDE**.
- A coluna `Status` do CFTV (OK, Erro no SD, 1 ou + cam Off, 100% Offline, Câmera Inexistente, Câmera Travada, Em espera por câmera/material, Infiltração, Manutenção/Sem Transmissão, Vandalismo, Substituição de câmera/TDM/UCP) NÃO define a cor; é exibida no tooltip/painel como "Status operacional (CFTV)" e é filtro (Q9).
- Registro sem nenhuma câmera existente (todas `-`/vazias) → "SEM CÂMERAS" (branco); texto não reconhecido → "INDEFINIDO" (roxo) e listado na auditoria (hoje: 0 casos).

### 5.3 Ausência de informação (§7)
Período principal: **01/09/2026 a 24/09/2026 — TODAS as datas aparecem** (inclusive 05, 06, 07, 12, 13, 14, 19, 20/09, que não têm arquivo). Prefixo sem registro na data → célula **BRANCA = SEM DADOS**. Nunca OFFLINE, erro, zero ou indisponibilidade. (Ex.: SANTA BRIGIDA inteira fica branca em 04/09 porque não está no arquivo.)

## 6. Relacionamento com a manutenção (§11–§17)
- Fonte das manutenções: **somente** o formulário Revisão_CFTV (a coluna "Manutenção" do CFTV é auxiliar — Q10).
- Chave: `Prefixo` (coluna do formulário) + data do formulário. Prefixo do formulário que não existe no CFTV (hoje: 11435) aparece como manutenção sem CFTV (branco + azul) e é listado na auditoria.
- Ler TODA a planilha: todos os cabeçalhos, linhas, textos longos e quebras de linha. Não truncar. Não escolher antecipadamente colunas importantes.
- Interpretar também o texto livre (§13): câmera mencionada e número, cabeamento, substituições, ativações, peças, nº de série, MAC, equipamento instalado, equipamento retirado, pendências, observações.
- Identificação de câmera no texto (§14): "Camera 21", "Câmera 21", "Câmara 21", "Cam 21", "Câmeras 22 e 23", "câmeras 21, 22 e 24" etc. → câmeras 21, 22, 23… Mostrado como **"Câmera informada pelo técnico no texto: Camera 21 → FRONTAL (câm 21)"** (mapeamento confirmado, Q3). As colunas "Problemas Detectados/Ações: Câm. <posição>" são ligadas às câmeras 21–26 pelo mesmo mapeamento. Notação "C1…C6" é exibida como "Notação informada pelo técnico", sem conversão (Q3/Q15).
- Técnicos: unificação apenas por maiúsculas/minúsculas ("Abner melo" → "Abner Melo"); o nome original fica visível no painel.
- Alertas por formulário (painel + auditoria): ID genérico 32500; ID citado no texto ≠ coluna ID (linha 236); outro prefixo citado no texto (linhas 191 e 196 — mantido o valor da coluna Prefixo); prefixo inexistente no CFTV (11435).
- Implementação: `scripts/cftv/manutencao.py` → `data/processed/manutencoes_tratadas.csv/.xlsx` (todas as respostas originais preservadas).
- Indicador visual (§15): **bolinha azul-escura sobre a célula** no dia da manutenção. A cor da célula continua sendo a do CFTV (vermelho+azul, laranja+azul, verde+azul, branco+azul = manutenção sem registro CFTV). A bolinha não altera o status.
- Várias manutenções no mesmo prefixo+dia (§16): nunca sobrescrever; mostrar contador (🔵 2); ao clicar, listar todas. (Hoje: 11 prefixos com 2 formulários no mesmo dia.)
- Painel da manutenção (§17): MANUTENÇÃO (Prefixo, Data, Hora, Técnico, Empresa, Garagem); ANOMALIAS ENCONTRADAS; CÂMERAS MENCIONADAS; AÇÕES REALIZADAS; PEÇAS/EQUIPAMENTOS; EQUIPAMENTO INSTALADO (nº série, MAC); EQUIPAMENTO RETIRADO (nº série, MAC); PENDÊNCIAS; OBSERVAÇÃO COMPLETA DO TÉCNICO; DEMAIS RESPOSTAS DO FORMULÁRIO. Toda coluna preenchida acessível; vazias podem ser ocultadas.

## 7. Regras de antes/depois (§18–§20, §24)
- Para cada manutenção: ANTES; DIA DA MANUTENÇÃO; 1º, 2º, 3º… REGISTRO POSTERIOR até 24/09/2026 (ou até o limite disponível da base quando a manutenção for fora do período).
- **ANTES** = último registro CFTV disponível antes da manutenção (ex.: manutenção 15/09, 14/09 sem dado, 13/09 com dado → usar 13/09; 14/09 continua em branco, nunca OFFLINE). Mostrar data, status geral e problema (ex.: "Câmera 21 OFFLINE").
- **DEPOIS** = primeiro registro disponível após a intervenção, e continuar acompanhando os seguintes. Registrar: normalizou (SIM/NÃO); 1º registro normal; permaneceu normal por N dias/registros; problema voltou (SIM/NÃO); data da recorrência; câmera da recorrência.
- Verde no dia seguinte NÃO é "resolvido definitivo".
- Duração (§24), quando possível: 1º dia do problema; último registro com problema antes; qtd de registros/dias com problema; data da manutenção; 1º registro normal após; tempo até normalizar; qtd de dias/registros normais depois; data e câmera da recorrência. **Sempre diferenciar DIAS CORRIDOS de REGISTROS DISPONÍVEIS.**
- **Registro do próprio dia (Q4):** exibido à parte ("No dia"); não conta como antes nem depois. A data usada é sempre a data literal do formulário (inclusive madrugada).
- **Evento** = prefixo + data (vários formulários no mesmo dia formam um evento). **Janela DEPOIS** = registros após a data até a véspera da próxima manutenção do mesmo prefixo (ou até 24/09). Se a próxima manutenção vier antes de qualquer registro posterior → SEM DADOS PARA VALIDAR.
- **Câmeras avaliadas** = câmeras com problema (OFFLINE ou ONLINE COM ERRO) no registro ANTES. Cada câmera recebe: RESOLVIDO (normalizou e não voltou), RECORRÊNCIA (normalizou e voltou a falhar na janela) ou NÃO RESOLVIDO (não normalizou em nenhum registro posterior).
- Implementação: `scripts/cftv/analise.py` → `data/processed/manutencao_x_cftv`, `analise_antes_depois`, `recorrencias` (.csv/.xlsx), com a "história" de cada evento em frases.

## 8. Critérios de resultado (§21, §22)
Classificações transparentes, sempre mostrando os dados usados; sem julgamento subjetivo:
- **RESOLVIDO**: o problema desapareceu e não voltou no período posterior observado.
- **RESOLVIDO COM RECORRÊNCIA**: normalizou, mas o mesmo problema/câmera voltou depois.
- **NÃO RESOLVIDO**: o problema permaneceu nos registros posteriores.
- **PARCIALMENTE RESOLVIDO**: havia múltiplos problemas e só parte foi corrigida.
- **PENDÊNCIA**: marcador separado do resultado (Q18) — o formulário registra pendência (critério §8.1).
- **SEM DADOS PARA VALIDAR**: sem registro ANTES, sem registro DEPOIS, manutenção fora do período, prefixo ausente do CFTV, nova manutenção antes do próximo registro, **ou veículo sem problema no CFTV antes (Q17 – marcador "Veículo já estava normal antes da manutenção")**.
- Recorrência (§22): diferenciar MESMA câmera × OUTRA câmera. Mesma câmera volta a falhar → "RECORRÊNCIA NA MESMA CÂMERA". Câmera original normalizada e outra câmera com problema → **não é recorrência**: "Problema original normalizado. Novo problema identificado em outra câmera."
- **Resultado do evento a partir das câmeras avaliadas:** todas RESOLVIDO → RESOLVIDO; nenhuma NÃO RESOLVIDO e ≥1 RECORRÊNCIA → RESOLVIDO COM RECORRÊNCIA; todas NÃO RESOLVIDO → NÃO RESOLVIDO; mistura com ≥1 NÃO RESOLVIDO e ≥1 normalizada → PARCIALMENTE RESOLVIDO.
- Problema surgido depois em câmera que estava normal antes → informado como "problema novo em outra câmera" (não altera o resultado; não é recorrência).
- **Taxa de resolução** = RESOLVIDO ÷ (RESOLVIDO + RESOLVIDO COM RECORRÊNCIA + NÃO RESOLVIDO + PARCIALMENTE RESOLVIDO). SEM DADOS PARA VALIDAR fica fora do denominador. Hoje: 55 ÷ 151 = 36,4%. Referência adicional (não é a taxa oficial): "normalizou" = (RESOLVIDO + COM RECORRÊNCIA) ÷ validáveis = 67 ÷ 151 = 44,4%.
- Resultado atual (313 eventos / 324 formulários): RESOLVIDO 55 · RESOLVIDO COM RECORRÊNCIA 12 · NÃO RESOLVIDO 69 · PARCIALMENTE RESOLVIDO 15 · SEM DADOS PARA VALIDAR 162 (100 já normais antes; 41 sem registro posterior; 13 fora do período; 5 sem registro anterior; 2 nova manutenção antes do próximo registro; 1 prefixo fora do CFTV). Pendência: 17 eventos. Problema novo em outra câmera: 19 eventos.

### 8.1 Detecção de PENDÊNCIA (Q16)
Marcação por palavras-chave (sem acento/maiúsculas), linha a linha da observação, exibindo o trecho e o termo encontrado:
`pendente`, `pendência(s)`, `aguardand…`, `não foi possível`, `falta`, `faltando`, `necessário/necessária`, `necessit…`, `precis… (de) (um/uma) nov…/troc…/substitu…/reposi…/cart…/câmera`; e a ação marcada no formulário **"Câmera encaminhada para manutenção"**.
Casos limítrofes conhecidos: a linha 80 do formulário foi marcada por um termo genérico e foi mantida (o trecho fica visível para a usuária julgar).

## 9. Regras visuais (§8–§10, §15, §23, §25–§31, §42–§44)
- **Matriz/heatmap**: linhas = prefixos; colunas = 01/09 a 24/09 (todas as datas). Célula inteira colorida: VERDE (todas ONLINE sem error), LARANJA (nenhuma OFFLINE e existe ONLINE com error), VERMELHO (≥1 OFFLINE), BRANCO (sem registro). Bolinha azul = manutenção (contador se >1).
- **Tooltip**: Prefixo, Data, Status geral e cada câmera (ex.: "Câmera 21 — ONLINE; Câmera 23 — ONLINE COM ERRO / SD: error / Gravação: error"). Nunca só o consolidado.
- **Clique na célula**: painel com PREFIXO, DATA, EMPRESA/GARAGEM, STATUS GERAL, CÂMERAS (nome, status, SD, Login, Gravação).
- **Clique no prefixo**: linha do tempo com a sequência diária (🟢/🟠/🔴/⚪ + 🔵) e eventos (câmera ficou OFFLINE, manutenção com técnico/intervenção, voltou ONLINE, ficou OFFLINE novamente, resultado).
- **Filtro "Câmera com problema"**: mostra veículos em que aquela câmera esteve OFFLINE ou com erro em algum dia do período. "Status do dia" + "Data": status naquela data (sem data: em qualquer dia).
- **Filtros**: Prefixo, Empresa, Garagem, Câmera, Status, Data, Técnico; com/sem manutenção; com OFFLINE; com erro; 100% normal; Resolvido; Resolvido com recorrência; Não resolvido; Parcialmente resolvido; Pendência; Sem dados para validar.
- **Cards**: Veículos analisados; Câmeras analisadas; Veículos com OFFLINE; Veículos com erro; Manutenções realizadas; Veículos que receberam manutenção; Resolvidos; Resolvidos com recorrência; Não resolvidos; Com pendência; Sem dados para validar; Taxa de resolução (só quando matematicamente válida, com a fórmula visível).
- **Efetividade** (§27): total de intervenções e cada classificação; análise por Técnico, Empresa, Garagem, Câmera, Tipo de problema, Tipo de intervenção. **Sem ranking depreciativo de técnicos**, apenas métricas objetivas.
- **Problemas recorrentes** (§28): prefixos com maior recorrência; câmeras com mais OFFLINE; com mais error; tipos de erro (SD, Login, Gravação); problemas que voltaram após manutenção.
- **Busca** "Buscar prefixo..." filtrando imediatamente.
- **Experiência da matriz**: 1ª coluna fixa; cabeçalho fixo; rolagem horizontal/vertical; células compactas; zoom/ajuste; filtros rápidos; ver vários prefixos ao mesmo tempo.
- **Legenda fixa**: VERDE todas ONLINE sem erro; LARANJA ONLINE com erro e nenhuma OFFLINE; VERMELHO pelo menos uma OFFLINE; BRANCO sem informação CFTV; BOLINHA AZUL houve manutenção.
- **Auditoria** (§33): DADO ORIGINAL → DADO INTERPRETADO (ex.: "ONLINE (SD: error, Login: ok, Gravação: error)" → Conectividade ONLINE, SD ERROR, Login OK, Gravação ERROR, Classificação ONLINE COM ERRO, Cor LARANJA) + lista de inconsistências (docs/DIAGNOSTICO.md §11).
- **Exportação** (§35): Excel/CSV dos resultados filtrados — Resumo; Histórico por prefixo; Manutenções; Resultado das manutenções; Recorrências.
- **Design**: moderno, corporativo, clean; fundo claro; cards discretos; bordas suaves; sem gradientes exagerados/sombras fortes/cards gigantes; cores de status fáceis de identificar. Prioridade desktop; utilizável em telas menores; no celular rolagem horizontal da matriz.
- **Desempenho**: milhares de registros sem travar (hoje 82.109 registros, 5.429 prefixos × 24 dias). Pré-processar em Python; não recalcular tudo a cada interação.

## 10. Regras de publicação (§36–§39)
- Dashboard web estático (Vite + JavaScript puro, ver §16 D8), funcionando no navegador sem Python/Node/Excel/servidor para quem abre o link.
- Projeto Git + repositório GitHub + hospedagem gratuita (GitHub Pages, Vercel ou similar) com URL pública HTTPS. Informar REPOSITÓRIO e DASHBOARD.
- Antes de publicar: verificar dados pessoais, credenciais, senhas, tokens, chaves, informações internas sensíveis. Nunca publicar senhas/tokens/.env/chaves. `.gitignore` adequado (inclusive `data/raw/`).
- Os dados operacionais serão publicados de forma consciente (Q12 autorizou dados completos). **Dados que ficam PÚBLICOS** (no site e no repositório):
  - `site/public/data/*.json` (e o site publicado): prefixos; empresa (CFTV) por dia; status de cada câmera 21–26 por dia (código compacto); status operacional e "última manutenção" do CFTV; nome do arquivo e linha de origem; formulários completos — prefixo, técnico (nome), data/hora, ID, garagem, tecnologia, todas as respostas das colunas de problemas/ações/quantidades, **observação integral**, números de série e MACs extraídos, alertas; resultados/histórias calculados.
  - `data/processed/` versionado: `cftv_consolidado.xlsx`, `manutencoes_tratadas`, `manutencao_x_cftv`, `analise_antes_depois`, `recorrencias`, `resumo_arquivos`, `inconsistencias`, `CHECKSUMS_SHA256_raw.txt` (mesmo conteúdo acima em planilhas).
  - Documentação (`docs/`, incluindo os arquivos de diagnóstico com trechos dos formulários) e capturas de tela.
  - **NÃO versionados:** planilhas originais `data/raw/*.xlsx` (ficam só na máquina local; o site não precisa delas), `cftv_consolidado.csv` (37 MB, recriado pelo script), arquivos intermediários `*.pkl`, `site/dist`, `node_modules`, venv, `.env*`, chaves/segredos (não há nenhum no projeto).

## 11. Atualização dos dados (§40)
Novos "Relatório CFTV" ou nova "Revisão_CFTV…" → copiar para `data/raw/` e executar `python scripts/atualizar_dados.py` (lê tudo de novo, regrava `data/processed/` e `site/public/data/`), depois `cd site && npm run build` (ou deixar o GitHub Actions publicar). Se houver mais de um arquivo Revisão_CFTV, o mais recente (pelo nome) é usado. Procedimento detalhado no README.md (COMO ATUALIZAR OS DADOS).

## 12. Testes obrigatórios (§45) e validação manual (§46)
1 todas ONLINE ok → VERDE · 2 uma ONLINE com error, nenhuma OFFLINE → LARANJA · 3 uma OFFLINE → VERMELHO · 4 sem registro → BRANCO · 5 Corredor + Corredor 1 → UMA câmera CORREDOR 1 · 6 manutenção em célula vermelha → fundo vermelho + marcador azul · 7 normaliza e volta → RESOLVIDO COM RECORRÊNCIA · 8 sem dado posterior → SEM DADOS PARA VALIDAR.
Validação manual: prefixos aleatórios — ARQUIVO ORIGINAL × CONSOLIDADO × DASHBOARD (datas, prefixos, status, conversão de Corredor, manutenção na data correta, textos não truncados, classificação pós-manutenção coerente).
Implementação: `tests/test_regras_obrigatorias.py` (casos 1–8 + regras das decisões Q2/Q4/Q17 etc.), `tests/test_visual.py` (caso 6 no site compilado, Playwright), `scripts/validacao_manual.py` → `docs/VALIDACAO.md`.

## 13. NÃO FAZER (§47)
Inventar status; preencher dias sem informação; transformar vazio em OFFLINE; tratar Corredor e Corredor 1 separadamente; usar abas de tabela/resumo; descartar observações; truncar textos longos; sobrescrever várias manutenções do mesmo veículo; considerar verde no dia seguinte como resolvido definitivo; considerar problema em outra câmera como recorrência da câmera reparada; alterar arquivos originais; publicar senha/token; deixar resultado só em localhost.

## 14. Fluxo obrigatório (§48)
F1 ler arquivos ✅ · F2 identificar estrutura/abas/colunas ✅ · F3 apresentar diagnóstico ✅ (`docs/DIAGNOSTICO.md`) · F4 criar REGRAS_PROJETO.md ✅ · F5 consolidar Relatórios CFTV ✅ · F6 interpretar status ✅ · F7 processar Revisão_CFTV ✅ · F8 relacionar manutenção + CFTV ✅ · F9 antes/depois/recorrência ✅ · F10 validar ✅ · F11 construir dashboard ✅ · F12 testar interatividade ✅ · F13 validar amostras contra Excel ✅ (`docs/VALIDACAO.md`) · F14 documentação ✅ · F15 publicar no GitHub · F16 publicar na web · F17 testar URL pública.

---

## 15. Achados do diagnóstico (resumo — detalhes em docs/DIAGNOSTICO.md)
- 16 Relatórios CFTV (01–04, 08–11, 15–18, 21–24/09); cada um com 2 abas: `Tabela` (ignorada) e `Relatório CFTV - DD.MM.2026` (usada). 82.109 registros; Data = nome do arquivo em 16/16; 0 duplicidades prefixo+data.
- **5.429 prefixos únicos no CFTV** (não ~200); 17 empresas. 306 prefixos receberam manutenção.
- Câmeras só por número (21–26), 4 textos distintos: ONLINE ok (215.730), `-` (110.100), OFFLINE (31.808), ONLINE com SD+Gravação error (17.732); 117.284 células vazias (fora da grade). Login nunca aparece com error.
- `-` é estável por prefixo/câmera e convive com Status "OK" → provavelmente "câmera não cadastrada/instalada nesse canal".
- Formulário: 324 respostas, 306 prefixos, 11/09 03:08 a 25/09 09:40; 14 nomes de técnicos; 11 garagens; 13 manutenções em 25/09; 44 em dias sem CFTV; prefixo 11435 não existe no CFTV; 18 prefixos com 2 formulários (11 no mesmo dia).
- Indício forte de mapeamento Câmera 21=FRONTAL, 22=FRENTE, 23=CORREDOR 1, 24=CORREDOR 2, 25=CORREDOR 3, 26=CORREDOR 4 (sem nenhuma contradição nos dados) — NÃO adotado sem confirmação.
- Manutenções da madrugada (00h–05h59) aparecem na coluna "Manutenção" do CFTV com a data do dia anterior (218 casos).

## 16. Decisões técnicas tomadas (já aplicadas, sem impacto em regra funcional)
- D1. Python 3.13 + pandas 3 + openpyxl em `/workspace/venv`; scripts numerados em `scripts/`.
- D2. Leitura com `data_only=True` (valores calculados), sem nunca salvar os arquivos de origem.
- D3. Linhas totalmente vazias no final das abas (só formatação) são desconsideradas; nenhuma linha com qualquer valor é descartada.
- D4. Cabeçalhos normalizados por Unicode NFC + trim + espaços múltiplos → 1 (resolve 'Câmera 21 ').
- D5. Empresa: trim dos espaços nas pontas.
- D6. Identificação de colunas do formulário pelo nome, nunca pela posição.
- D7. Toda linha consolidada guarda `arquivo_origem` e `linha_excel`.
- D8. **Site: Vite 5 + JavaScript puro (sem framework)** + SheetJS (xlsx) para exportação. Motivo: site 100% estático, leve (~110 KB gzip de JS), sem etapa de servidor; a matriz é desenhada com virtualização própria (só as linhas visíveis ficam na tela), suportando os 5.430 prefixos.
- D9. `base` do Vite = `./` (caminho relativo) por padrão, configurável por `BASE_PATH` (ex.: `/analise-cftv-manutencoes/`) → funciona no GitHub Pages em qualquer nome de repositório.
- D10. Pré-processamento em Python gera JSON compacto em `site/public/data/` (cftv.json ≈ 2,3 MB com códigos de 1 caractere por câmera/dia; manutencoes.json ≈ 1,9 MB; meta.json). Nenhum servidor é necessário.
- D11. Script único de atualização `scripts/atualizar_dados.py` (≈ 1 min).
- D12. Planilhas originais (`data/raw/*.xlsx`) **não** vão para o repositório (não são necessárias para o site; checksums em `data/processed/CHECKSUMS_SHA256_raw.txt`). `cftv_consolidado.csv` também não (37 MB; a versão .xlsx é versionada).
- D13. Linha "Com manutenção": prefixo 11435 (fora do CFTV) aparece na matriz com linha branca + bolinha; por isso "Todos os veículos" mostra 5.430 linhas (5.429 do CFTV + 1).

---

## 17. DECISÕES DA USUÁRIA – 25/09/2026
Respostas da Letícia às questões Q1–Q19 do diagnóstico. **Estas decisões são regras do projeto** e prevalecem sobre as recomendações anteriores.

| Q | Tema | Decisão | Como foi implementado |
|---|---|---|---|
| Q1 | Escopo da matriz | (sem resposta explícita → padrão recomendado) Processar **todos os 5.429 prefixos**; a matriz abre filtrada em **"Com manutenção" (306)**, com opção "Todos" e "Sem manutenção". Desempenho garantido com renderização virtualizada de linhas. | Filtro "Veículos" (Com manutenção / Todos / Sem manutenção); matriz virtualizada |
| Q2 | Significado de `-` | **`-` = o veículo NÃO possui aquela câmera (não instalada).** A câmera não existe para aquele prefixo naquele dia: fica **fora da lista de câmeras**, nunca conta como OFFLINE/erro, nunca afeta a cor. "sem câmera" aparece **somente na auditoria**. | Código `-` → "SEM CÂMERA"; excluída de tooltip/painel/contagens; visível só na aba Auditoria |
| Q3 | Câmera 21–26 × posição | **MAPEAMENTO CONFIRMADO:** Câmera 21 = FRONTAL · 22 = FRENTE · 23 = CORREDOR 1 · 24 = CORREDOR 2 · 25 = CORREDOR 3 · 26 = CORREDOR 4. Aplicar em todo lugar exibindo posição + número (ex.: "CORREDOR 1 (câm 23)"). Usar para ligar as colunas de problemas/ações por posição do formulário e as menções "Camera 21" do texto livre às câmeras do CFTV, permitindo recorrência na mesma câmera × outra câmera. **Notação "C1…C6": não mapear automaticamente**, a menos que o contexto seja inequívoco; exibir como informado pelo técnico. | Mapeamento fixo em `scripts/cftv/config.py`; C1…C6 exibido como "Notação informada pelo técnico" (nenhum caso inequívoco foi encontrado → nenhum mapeado) |
| Q4 | Registro do dia da manutenção | **Bolinha na data literal do formulário.** O registro CFTV desse dia é exibido separadamente ("DIA DA MANUTENÇÃO") e **não conta como antes nem como depois**. | ANTES = último registro com data < data da manutenção; DEPOIS = registros com data > data da manutenção |
| Q5 | Repetições | (padrão) Mesmo prefixo + mesmo dia → **um evento** (intervenção) com contador 🔵 N e todas as respostas listadas; uma classificação por evento. Dias diferentes → cada evento é avaliado com janela DEPOIS até a véspera da próxima manutenção do mesmo prefixo. Prefixo+data duplicado no CFTV (hoje 0) → manter ambos, sinalizar na auditoria, usar a pior situação para a cor. | `scripts/cftv/analise.py` |
| Q6 | Fora do período / dias sem arquivo | (padrão) 12, 14, 19, 20/09 → célula branca + bolinha. **25/09 → coluna extra "25/09 (fora do período)" só com bolinha** (sem cor CFTV); classificação **SEM DADOS PARA VALIDAR**; ANTES = último registro disponível. | Colunas extras geradas automaticamente para datas de manutenção após 24/09 |
| Q7/Q8 | 14/09 e Santa Brígida em 04/09 | **Não existe arquivo → branco (sem dados).** | — |
| Q9 | Coluna Status do CFTV | (padrão) **Cor sempre pelo texto das câmeras**; Status exibido no tooltip/painel e como filtro "Status operacional (CFTV)". | — |
| Q10 | Coluna "Manutenção" do CFTV | (padrão) **Só informação extra** ("Última manutenção segundo o CFTV"); não gera bolinha. | — |
| Q11 | Prefixo/ID divergente no formulário | (padrão) **Manter o valor da coluna Prefixo**; sinalizar as linhas 191 e 196 (e ID da linha 236, ID genérico 32500) na auditoria e no painel da manutenção. | Alertas por formulário |
| Q12 | Dados públicos | **Pode publicar os dados completos** (nomes de técnicos, nº de série/MAC, textos livres, prefixos). Nunca publicar segredos/tokens/.env. Documentar exatamente quais dados ficam públicos (README e §10). | — |
| Q13 | Nomes de técnicos | (padrão) Unificar **apenas a diferença de maiúsculas** ("Abner melo" → "Abner Melo"); "Lui" permanece separado. | Regra genérica: nomes iguais ignorando maiúsculas/minúsculas → grafia mais frequente |
| Q14 | Empresa × Garagem | (padrão) Manter os dois campos; filtro EMPRESA = CFTV (empresa do registro de cada dia; rótulo da linha = empresa mais recente); filtro GARAGEM = formulário. | — |
| Q15 | C1…C6 | Ver Q3: não mapear automaticamente; exibir como informado. | — |
| Q16 | Pendência | (padrão) Detectar por **palavras-chave** no texto livre + ação "Câmera encaminhada para manutenção", **mostrando o trecho que gerou a marcação**. | Lista de termos em §8.1 |
| Q17 | Veículo já normal antes | **Não criar nova classe de resultado.** Exibir um **marcador/nota informativa destacada: "Veículo já estava normal antes da manutenção"**. Resultado formal o mais fiel possível à especificação: como não havia problema no CFTV para ser corrigido, não se pode afirmar RESOLVIDO → resultado formal **SEM DADOS PARA VALIDAR** (motivo: "sem problema no CFTV antes da manutenção"), com o marcador em destaque e a indicação se surgiu problema depois. | §8 |
| Q18 | Precedência | (padrão) Resultado principal pelo CFTV (RESOLVIDO / RESOLVIDO COM RECORRÊNCIA / NÃO RESOLVIDO / PARCIALMENTE RESOLVIDO / SEM DADOS PARA VALIDAR) + **PENDÊNCIA como marcador separado**. PARCIALMENTE RESOLVIDO quando, entre as câmeras com problema no ANTES, algumas normalizaram e outras não. | §8 |
| Q19 | Anomalia ALFA RODOBUS | (padrão) Manter o dado original e **sinalizar na auditoria**. | — |

## 18. QUESTÕES EM ABERTO
Nenhuma questão pendente de decisão neste momento. Novas dúvidas devem ser registradas aqui antes de qualquer decisão.

---

## 19. Histórico de decisões
| Data | Decisão | Origem |
|---|---|---|
| 25/09/2026 | Criação do documento (Fases 1–4). Regras D1–D7. Questões Q1–Q19 abertas. | Diagnóstico inicial |
| 25/09/2026 | Decisões da usuária Q1–Q19 registradas (§17); QUESTÕES EM ABERTO esvaziada. | Letícia |
| 25/09/2026 | Fases 5–14 concluídas: regras detalhadas nas seções 4–12 e D8–D13; lista de dados públicos em §10; taxa de resolução em §8. Publicação (F15–F17) aguardando login do GitHub. | Execução |

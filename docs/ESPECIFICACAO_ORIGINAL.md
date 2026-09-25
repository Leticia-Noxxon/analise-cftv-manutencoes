# PROJETO: ANÁLISE CFTV + MANUTENÇÕES
(Especificação original enviada pela usuária Letícia em 25/09/2026. Texto integral das regras; seguir literalmente.)

Dashboard interativo para análise de câmeras de veículos antes e depois das manutenções.

## REGRA Nº 1 – LEIA E DOCUMENTE ANTES DE PROGRAMAR
Antes de criar, alterar, corrigir ou atualizar QUALQUER parte deste projeto:
1. Leia este documento inteiro.
2. Leia o arquivo REGRAS_PROJETO.md do projeto, caso já exista.
3. Analise os arquivos reais antes de definir qualquer regra adicional.
4. Não altere regras já estabelecidas silenciosamente.
5. Não invente informações ausentes.
6. Não elimine dados dos arquivos de origem.
7. Não simplifique a lógica sem autorização.
8. Toda nova regra ou alteração estrutural deverá ser registrada em REGRAS_PROJETO.md.

Crie obrigatoriamente na raiz do projeto: REGRAS_PROJETO.md, documentando: objetivo do projeto; arquivos utilizados; estrutura encontrada; nomes das colunas; regras de consolidação; regras de status; regra de "Corredor" = "Corredor 1"; relacionamento com manutenção; regras de antes/depois; critérios de resolvido/não resolvido; regras visuais; regras de publicação; decisões técnicas tomadas.
ANTES DE TODA FUTURA ALTERAÇÃO NO PROJETO: LER NOVAMENTE REGRAS_PROJETO.md.

## 1. OBJETIVO
Analisar aproximadamente 200 câmeras/veículos monitorados pelo CFTV. Descobrir visualmente: como cada veículo estava em cada dia; quais câmeras estavam ONLINE; quais OFFLINE; quais ONLINE mas com erro; quando foi realizada manutenção; qual câmera apresentou problema; o que o técnico encontrou; o que o técnico fez; se existia pendência; como a câmera ficou depois; se a manutenção resolveu; se resolveu apenas temporariamente; se o problema voltou; quantos dias demorou para normalizar; quantos dias permaneceu normal depois da manutenção.
Objetivo principal: ANTES → MANUTENÇÃO → DEPOIS → RECORRÊNCIA.

## 2. ARQUIVOS CFTV
Na pasta existem vários arquivos cujo nome começa com "Relatório CFTV". Localize TODOS. Cada arquivo pode possuir mais de uma aba. NÃO consolidar todas as abas. Usar SOMENTE A ABA QUE CONTÉM OS DADOS/INFORMAÇÕES DO CFTV. Abas de tabela, resumo, gráfico, dashboard, tabela dinâmica, apresentação, consolidação visual devem ser IGNORADAS se não forem a base original dos registros.
Antes de decidir: liste todas as abas; analise cabeçalhos; analise algumas linhas; identifique automaticamente a aba com os registros reais.
Registrar em REGRAS_PROJETO.md: arquivo; aba utilizada; abas ignoradas; motivo.

## 3. CONSOLIDAÇÃO
Juntar todas as abas válidas em uma única base. Antes de concatenar: analisar cabeçalhos; identificar diferenças; padronizar nomes; preservar dados; não descartar colunas relevantes; identificar duplicidades; identificar campos equivalentes.
REGRA OBRIGATÓRIA: "Corredor" e "Corredor 1" SÃO A MESMA CÂMERA. Padronizar ambos como CORREDOR 1. Nunca criar Corredor e Corredor 1 como duas câmeras diferentes.
Câmeras podem aparecer como FRONTAL, FRENTE, CORREDOR 1, CORREDOR 2, CORREDOR 3, CORREDOR 4. Não assumir quantidade fixa de câmeras. Utilizar exatamente as câmeras existentes para cada veículo.

## 4. FORMATO REAL DOS STATUS
Exemplos reais: "ONLINE (SD: ok, Login: ok, Gravação: ok)", "ONLINE (SD: error, Login: ok, Gravação: error)", "OFFLINE". O sistema deve interpretar o conteúdo do texto.

## 5. CLASSIFICAÇÃO INDIVIDUAL DA CÂMERA
- NORMAL: ONLINE (SD: ok, Login: ok, Gravação: ok) → ONLINE NORMAL, cor VERDE.
- ONLINE COM ERRO: ex. ONLINE (SD: error, Login: ok, Gravação: error) → ONLINE COM ERRO, cor LARANJA. Basta pelo menos um campo com "error" (SD, Login, Gravação). Preservar quais erros ocorreram (ex.: Erros: SD, Gravação).
- OFFLINE → OFFLINE, cor VERMELHO.

## 6. STATUS GERAL DO VEÍCULO NO DIA
Analisar TODAS as câmeras do prefixo na data. Prioridade: 1º OFFLINE, 2º ONLINE COM ERRO, 3º ONLINE NORMAL.
Se pelo menos UMA câmera OFFLINE → VERMELHO (mesmo que as outras estejam ONLINE). Se nenhuma OFFLINE mas pelo menos uma ONLINE COM ERRO → LARANJA. Somente se TODAS ONLINE com SD ok, Login ok, Gravação ok → VERDE.

## 7. AUSÊNCIA DE INFORMAÇÃO
Período principal: 01/09/2026 até 24/09/2026. TODAS as datas devem aparecer. Se o prefixo não possuir registro na data: DEIXAR EM BRANCO. NÃO considerar OFFLINE, erro, zero, indisponibilidade. Ausência = SEM DADOS.

## 8. MATRIZ PRINCIPAL
HEATMAP/MATRIZ INTERATIVA. Linhas: prefixos. Colunas: 01/09 até 24/09. A CÉLULA INTEIRA recebe a cor. VERDE = todas ONLINE sem error. LARANJA = nenhuma OFFLINE, existe ONLINE com error. VERMELHO = pelo menos uma OFFLINE. BRANCO = sem registro.

## 9. TOOLTIP
Ao passar o mouse: Prefixo, Data, Status geral, e cada câmera (ex.: FRONTAL — ONLINE; CORREDOR 1 — OFFLINE; CORREDOR 3 — ONLINE COM ERRO / SD: error / Gravação: error). Não mostrar somente o status consolidado.

## 10. CLIQUE NA CÉLULA
Abrir painel lateral/modal: PREFIXO, DATA, EMPRESA/GARAGEM se existir, STATUS GERAL, CÂMERAS; para cada câmera: Nome, Status, SD, Login, Gravação (quando existirem no texto).

## 11. ARQUIVO DE MANUTENÇÃO
C:\Users\letic\Downloads\analise 200 câmeras 25092026\Revisão_CFTV2026-09-25_13_34_23.xlsx — respostas do formulário dos técnicos. LER TODA A PLANILHA: todos os cabeçalhos, todas as linhas, todo texto, campos longos, observações, quebras de linha. Não truncar textos. Não escolher antecipadamente quais colunas são importantes. Primeiro compreender a estrutura real.

## 12. EXEMPLO REAL DE MANUTENÇÃO
Técnico: John Lima; Data: sexta-feira, setembro 25, 2026 09:40; Empresa/Garagem: Viação Metrópole M'Boi Mirim; Problemas selecionados: Câmera inoperante, Cabeamento rompido/danificado; Ações: Substituição da câmera defeituosa, Substituição do cabeamento, Ativação da câmera. Outros campos podem ter "Nenhuma anomalia identificada", "Nenhuma ação realizada". Campo de observação com texto livre como:
"Anomalias / Camera 21 inoperante / Reparos / Substituído Cabeamento UTP e a Camera 21 / Número de série câmera instalada 210235UDL5F247002849 / MAC E4F14C780CBE / RETIRADA 210A235UGNJ324A003395 / MAC E4F14C7F1524". Esse texto NÃO pode ser descartado.

## 13. INTERPRETAÇÃO DA MANUTENÇÃO
Analisar: prefixo; técnico; data; horário; empresa; garagem; problemas; anomalias; ações; câmera mencionada; número da câmera; cabeamento; substituições; ativações; peças; número de série; MAC; equipamento instalado; equipamento retirado; pendências; observações; texto livre; todos os demais campos. Não depender só das colunas estruturadas; analisar também texto livre.

## 14. IDENTIFICAÇÃO DA CÂMERA NA MANUTENÇÃO
"Camera 21", "Câmera 21", "Cam 21" e variações: identificar a câmera mencionada. NÃO inventar correspondência entre "Camera 21" e posição (ex.: "Corredor 2") sem informação confiável nos arquivos. Se houver mapeamento disponível: usar. Caso contrário mostrar "Câmera informada pelo técnico: Camera 21" sem inventar posição.

## 15. INDICADOR VISUAL DE MANUTENÇÃO
No dia com manutenção: BOLINHA AZUL ESCURA SOBRE a célula. A cor da célula continua representando CFTV (vermelho+azul, laranja+azul, verde+azul, branco+azul = manutenção sem registro CFTV). A bolinha NÃO altera o status.

## 16. VÁRIAS MANUTENÇÕES NO MESMO DIA
Mesmo prefixo + mesma data: não sobrescrever. Mostrar contador (🔵 2). Ao clicar, listar todas as intervenções do dia.

## 17. PAINEL DA MANUTENÇÃO
Ao clicar no marcador: painel/modal organizado: MANUTENÇÃO (Prefixo, Data, Hora, Técnico, Empresa, Garagem); ANOMALIAS ENCONTRADAS; CÂMERAS MENCIONADAS; AÇÕES REALIZADAS; PEÇAS/EQUIPAMENTOS; EQUIPAMENTO INSTALADO (Número de série, MAC); EQUIPAMENTO RETIRADO (Número de série, MAC); PENDÊNCIAS; OBSERVAÇÃO COMPLETA DO TÉCNICO; DEMAIS RESPOSTAS DO FORMULÁRIO. Toda coluna preenchida deve ficar acessível. Campos vazios podem ser ocultados.

## 18. ANÁLISE TEMPORAL
Não só dia anterior vs seguinte. Para cada manutenção: ANTES; DIA DA MANUTENÇÃO; 1º, 2º, 3º... REGISTRO POSTERIOR ATÉ 24/09/2026 (ou até o limite disponível na base quando a manutenção ocorrer fora do período).

## 19. ANTES
Registro CFTV imediatamente anterior disponível (ex.: manutenção 15/09, 14/09 sem dado, 13/09 com dado → usar 13/09; não transformar 14/09 em OFFLINE). Mostrar ÚLTIMO REGISTRO ANTES DA MANUTENÇÃO, data, status geral, problema (ex.: CORREDOR 1 OFFLINE).

## 20. DEPOIS
Primeiro registro disponível depois da intervenção; continuar acompanhando os seguintes. Ex.: 15/09 🔴🔵, 16 🟢, 17 🟢, 18 🟢, 19 🔴 → não classificar simplesmente como RESOLVIDO. Registrar: Normalizou após manutenção: SIM; Primeiro registro normal: 16/09; Permaneceu normal: 3 dias/registros; Problema voltou: SIM; Data da recorrência: 19/09.

## 21. RESULTADO DA MANUTENÇÃO (classificações transparentes)
- RESOLVIDO: problema desapareceu e não voltou no período posterior observado.
- RESOLVIDO COM RECORRÊNCIA: normalizou, mas o mesmo problema/câmera voltou depois.
- NÃO RESOLVIDO: problema permaneceu nos registros posteriores.
- PARCIALMENTE RESOLVIDO: havia múltiplos problemas e só parte foi corrigida.
- PENDÊNCIA: formulário registra explicitamente pendência relevante.
- SEM DADOS PARA VALIDAR: não existem registros posteriores suficientes.
Não usar julgamento subjetivo. Mostrar sempre os dados usados para a classificação.

## 22. DIFERENCIAR RECORRÊNCIA
Identificar se voltou A MESMA CÂMERA ou OUTRA. Ex.: antes Corredor 1 OFFLINE, depois ONLINE, 5 dias depois Corredor 1 OFFLINE → RECORRÊNCIA NA MESMA CÂMERA. Ex.: antes Corredor 1 OFFLINE, depois Corredor 1 ONLINE e Corredor 3 OFFLINE → não chamar de recorrência; registrar "Problema original normalizado. Novo problema identificado em outra câmera."

## 23. LINHA DO TEMPO
Ao clicar no PREFIXO: página/painel de histórico com sequência diária (🟢/🔴/🔵) e eventos abaixo (ex.: 03/09 Corredor 1 ficou OFFLINE; 06/09 MANUTENÇÃO Técnico/Intervenção; 07/09 Corredor 1 voltou ONLINE; 10/09 Corredor 1 ficou OFFLINE novamente; Resultado: RESOLVIDO COM RECORRÊNCIA).

## 24. DURAÇÃO DOS PROBLEMAS
Quando possível: primeiro dia do problema; último registro com problema antes da manutenção; quantidade de registros/dias com problema; data da manutenção; primeiro registro normal após; tempo para normalização; quantidade de dias/registros normais depois; data da recorrência; câmera da recorrência. Diferenciar DIAS CORRIDOS de REGISTROS DISPONÍVEIS.

## 25. FILTROS
Conforme campos disponíveis: PREFIXO, EMPRESA, GARAGEM, CÂMERA, STATUS, DATA, TÉCNICO; Com/Sem manutenção; Com OFFLINE; Com erro; 100% normal; Resolvido; Resolvido com recorrência; Não resolvido; Parcialmente resolvido; Pendência; Sem dados para validar.

## 26. INDICADORES (cards no topo)
VEÍCULOS ANALISADOS; CÂMERAS ANALISADAS; VEÍCULOS COM OFFLINE; VEÍCULOS COM ERRO; MANUTENÇÕES REALIZADAS; VEÍCULOS QUE RECEBERAM MANUTENÇÃO; RESOLVIDOS; RESOLVIDOS COM RECORRÊNCIA; NÃO RESOLVIDOS; COM PENDÊNCIA; SEM DADOS PARA VALIDAR; TAXA DE RESOLUÇÃO quando matematicamente válido, mostrando claramente a fórmula.

## 27. EFETIVIDADE DAS MANUTENÇÕES
Total de intervenções; Resolvidas; Resolvidas com recorrência; Não resolvidas; Parcialmente resolvidas; Pendentes; Sem dados posteriores. Análise por Técnico, Empresa, Garagem, Câmera, Tipo de problema, Tipo de intervenção. Não criar ranking depreciativo de técnicos; apenas métricas objetivas.

## 28. PROBLEMAS RECORRENTES
Prefixos com maior recorrência; câmeras com mais OFFLINE; câmeras com mais error; tipos de erro (SD, Login, Gravação); problemas que voltaram após manutenção.

## 29. BUSCA
Campo "Buscar prefixo..." filtrando imediatamente.

## 30. EXPERIÊNCIA DA MATRIZ
Primeira coluna fixa; cabeçalho fixo; rolagem horizontal e vertical; células compactas; tooltip; zoom/ajuste se necessário; filtros rápidos. Não criar células gigantes; ver vários prefixos simultaneamente.

## 31. LEGENDA FIXA
VERDE todas ONLINE sem erro; LARANJA ONLINE com erro e nenhuma OFFLINE; VERMELHO pelo menos uma OFFLINE; BRANCO sem informação CFTV; BOLINHA AZUL houve manutenção.

## 32. VALIDAÇÃO ANTES DO DASHBOARD (diagnóstico)
Quantidade de "Relatório CFTV"; nome de cada arquivo; abas existentes; aba escolhida; abas ignoradas; registros por arquivo; datas encontradas; prefixos encontrados; qtd prefixos únicos; colunas encontradas; colunas padronizadas; qtd registros de manutenção; prefixos na manutenção; prefixos da manutenção que NÃO existem no CFTV; datas de manutenção; técnicos; empresas/garagens; duplicidades; campos inesperados; dados inconsistentes.

## 33. AUDITORIA
Área AUDITORIA DOS DADOS: DADO ORIGINAL → DADO INTERPRETADO (ex.: Original "ONLINE (SD: error, Login: ok, Gravação: error)" → Conectividade ONLINE, SD ERROR, Login OK, Gravação ERROR, Classificação ONLINE COM ERRO, Cor LARANJA).

## 34. DADOS ORIGINAIS
Nunca substituir a base original. /data/raw (originais, nunca alterar) e /data/processed (tratados).

## 35. EXPORTAÇÃO
Exportar resultados filtrados para Excel/CSV: Resumo; Histórico por prefixo; Manutenções; Resultado das manutenções; Recorrências.

## 36. TECNOLOGIA
DASHBOARD WEB no navegador: rápido, responsivo, simples, fácil de compartilhar, sem depender de Excel, filtros no navegador. Ex.: HTML/CSS/JS, React, Vite. Explicar a escolha.

## 37. PUBLICAÇÃO ONLINE
Não pode ficar só em localhost/arquivo local. Criar projeto Git; repositório no GitHub; publicar código; configurar hospedagem (GitHub Pages, Vercel ou outra gratuita); URL pública HTTPS. Informar REPOSITÓRIO: [link] e DASHBOARD: [link público].

## 38. ATENÇÃO COM DADOS PUBLICADOS
Antes de publicar verificar dados pessoais, credenciais, senhas, tokens, chaves, informações internas sensíveis. Nunca publicar senhas, tokens, credenciais, .env, chaves privadas. .gitignore adequado. Se os dados operacionais forem necessários, estruturar conscientemente e informar exatamente quais dados ficarão públicos. NÃO esconder esse fato.

## 39. FUNCIONAMENTO SEM SERVIDOR LOCAL
Outra pessoa abre o link e funciona, sem instalar Python/Node, sem Excel, sem servidor, sem baixar projeto.

## 40. ATUALIZAÇÃO DOS DADOS
Novos "Relatório CFTV" ou nova "Revisão_CFTV..." → reexecutar consolidação sem reconstruir o projeto. Documentar COMO ATUALIZAR OS DADOS.

## 41. DOCUMENTAÇÃO
README.md (descrição, instalação, execução, atualização, publicação, estrutura de pastas) e REGRAS_PROJETO.md (TODAS as regras funcionais deste documento).

## 42. DESIGN
Moderna, profissional, corporativa, clean. Fundo claro/branco, cards discretos, bordas suaves, tipografia profissional. Evitar gradientes exagerados, sombras fortes, cards gigantes, cores excessivas, decoração desnecessária. Cores de status facilmente identificáveis.

## 43. RESPONSIVIDADE
Prioridade desktop; utilizável em telas menores; no celular rolagem horizontal da matriz.

## 44. DESEMPENHO
Milhares de registros sem travar. Pré-processar. Não recalcular tudo a cada interação.

## 45. TESTES OBRIGATÓRIOS
1 todas ONLINE ok → VERDE. 2 uma ONLINE com error, nenhuma OFFLINE → LARANJA. 3 uma OFFLINE → VERMELHO. 4 sem registro → BRANCO. 5 Corredor + Corredor 1 → UMA câmera CORREDOR 1. 6 manutenção em célula vermelha → fundo vermelho + marcador azul. 7 normaliza e volta → RESOLVIDO COM RECORRÊNCIA. 8 sem dado posterior → SEM DADOS PARA VALIDAR.

## 46. VALIDAÇÃO MANUAL
Selecionar prefixos aleatórios e comparar ARQUIVO ORIGINAL x CONSOLIDADO x DASHBOARD; idem manutenção. Confirmar datas, prefixos, status, conversão de Corredor, manutenção na data correta, textos não truncados, classificação pós-manutenção coerente.

## 47. NÃO FAZER
Inventar status; preencher dias sem informação; transformar vazio em OFFLINE; tratar Corredor e Corredor 1 separadamente; usar abas de tabela/resumo; descartar observações; truncar textos longos; sobrescrever várias manutenções do mesmo veículo; considerar verde no dia seguinte como resolvido definitivo; considerar problema em outra câmera como recorrência da câmera reparada; alterar arquivos originais; publicar senha/token; deixar resultado só em localhost.

## 48. FLUXO OBRIGATÓRIO
F1 ler arquivos; F2 identificar estrutura/abas/colunas; F3 apresentar diagnóstico; F4 criar REGRAS_PROJETO.md; F5 consolidar Relatórios CFTV; F6 interpretar status; F7 processar Revisão_CFTV; F8 relacionar manutenção + CFTV; F9 antes/depois/recorrência; F10 validar; F11 construir dashboard; F12 testar interatividade; F13 validar amostras contra Excel; F14 documentação; F15 publicar no GitHub; F16 publicar na web; F17 testar URL pública sem acesso a arquivos locais.

## 49. ENTREGA FINAL
Dashboard completo; base CFTV consolidada; base tratada das manutenções; relação manutenção × CFTV; análise antes/depois; análise de recorrência; matriz 01/09–24/09; filtros; timeline por prefixo; detalhamento das câmeras; detalhamento completo da manutenção; indicadores; auditoria; exportação; README.md; REGRAS_PROJETO.md; código-fonte; repositório GitHub; link público funcionando.

## 50. REGRA FINAL
Não é um gráfico bonito; é uma ferramenta de investigação. Para qualquer PREFIXO responder: como estava antes; qual câmera com problema; OFFLINE ou ONLINE com erro; qual erro; há quanto tempo; quando houve manutenção; quem realizou; anomalia; o que foi feito; qual câmera/equipamento substituído; número de série/MAC; pendência; como ficou no primeiro registro depois; continuou normal; por quantos dias/registros; o mesmo problema voltou; quando; mesma câmera ou outra; classificação pelos dados (resolvida, recorrente, não resolvida, parcial, sem dados). Tudo rastreável até os arquivos originais.
ANTES DE FAZER QUALQUER ALTERAÇÃO FUTURA: RELEIA REGRAS_PROJETO.md INTEIRO.

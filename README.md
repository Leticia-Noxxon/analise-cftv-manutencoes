# Análise CFTV × Manutenções

> **DASHBOARD:** https://leticia-noxxon.github.io/analise-cftv-manutencoes/
> **REPOSITÓRIO:** https://github.com/Leticia-Noxxon/analise-cftv-manutencoes
> Publicado em 25/09/2026 (GitHub Pages, atualizado automaticamente a cada push na branch `main`).

Painel web **estático** que mostra, dia a dia, a situação das câmeras de CFTV de cada veículo (prefixo) e o que aconteceu
**antes, no dia e depois** de cada manutenção registrada pelos técnicos. Assim dá para ver se o problema foi resolvido,
se voltou (recorrência) ou se continuou.

- Período do CFTV: **01/09/2026 a 06/10/2026** (17 relatórios diários: 01–24/09 e 06/10; as datas sem arquivo, inclusive 25/09–05/10, aparecem em branco).
- **5.466 veículos**, 17 empresas, **17.767 câmeras** instaladas, 87.329 registros diários.
- A partir de 06/10, as posições de câmera que não batem com o histórico do veículo são **reconciliadas com o histórico** (decisão da Letícia de 07/10/2026; veja "Reconciliação de câmeras" abaixo).
- **324 formulários de manutenção** → **313 eventos** (prefixo + data), em **306 veículos**.

![Matriz](docs/screenshots/01_matriz.png)

## O que o painel mostra

| Aba | Conteúdo |
|---|---|
| **Matriz** (principal) | Uma linha por prefixo, uma coluna por dia. Cor = situação das câmeras: 🟩 todas ONLINE sem erro · 🟧 alguma câmera ONLINE com erro (SD/Login/Gravação) · 🟥 alguma câmera OFFLINE · ⬜ sem dados. 🔵 bolinha azul = manutenção naquele dia (número = mais de um formulário). Passe o mouse para ver cada câmera; clique no quadrado (detalhe do dia), na bolinha (manutenção completa) ou no prefixo (linha do tempo). Abre filtrada em **“Com manutenção” (306)**; o botão **“Todos os veículos”** mostra os 5.467 prefixos (5.466 do CFTV + 1 prefixo só do formulário) sem travar (linhas virtualizadas). |
| **Manutenções** | Lista de todas as manutenções com técnico, câmeras com anomalia, situação antes e resultado. |
| **Efetividade** | Contagem por resultado, taxa de resolução (fórmula visível) e tabelas por técnico, empresa, garagem, câmera, tipo de problema e tipo de intervenção (ordem alfabética, sem ranking). |
| **Recorrências** | Casos em que a mesma câmera voltou a falhar, problemas novos em outra câmera, câmeras com mais dias OFFLINE/erro, tipos de erro e prefixos com mais dias com problema. |
| **Auditoria** | Texto original de cada câmera → interpretação, abas usadas/ignoradas em cada arquivo, inconsistências encontradas e resumo das regras. |
| **Como ler** | Explicação simples do painel. |

Exportação: **Exportar Excel** (planilhas Resumo, Histórico por prefixo, Manutenções, Resultado das manutenções, Recorrências — sempre com os filtros atuais) ou **CSV** de cada planilha.

### Resultado das manutenções

| Resultado | Quando | Eventos |
|---|---|---|
| RESOLVIDO | todas as câmeras com problema antes normalizaram e não voltaram a falhar | 79 |
| RESOLVIDO COM RECORRÊNCIA | normalizaram, mas a mesma câmera voltou a falhar | 27 |
| NÃO RESOLVIDO | nenhuma câmera com problema normalizou | 50 |
| PARCIALMENTE RESOLVIDO | parte normalizou, parte não | 18 |
| SEM DADOS PARA VALIDAR | sem registro antes/depois, fora do período, prefixo fora do CFTV ou **veículo já estava normal antes** (124 casos, com aviso destacado) | 139 |

**Taxa de resolução = RESOLVIDO ÷ (RESOLVIDO + RESOLVIDO COM RECORRÊNCIA + NÃO RESOLVIDO + PARCIALMENTE RESOLVIDO) = 79 ÷ 174 = 45,4%.**
Avisos separados (não mudam o resultado): **Pendência registrada** (17 eventos, com o trecho do formulário) e **Veículo já estava normal antes da manutenção**.
Regras completas: [`REGRAS_PROJETO.md`](REGRAS_PROJETO.md).

### Reconciliação de câmeras com o histórico (decisão de 07/10/2026)

No relatório de 06/10, parte dos veículos veio com a câmera numa coluna diferente da de sempre (por exemplo, a câmera
única da ALFA RODOBUS na coluna "Câmera 22" em vez de "Câmera 21"). Decisão da Letícia: **vale o histórico do veículo**,
para não perder os dados dos dias atuais. Regra (`scripts/cftv/reconciliacao.py`, datas a partir de 06/10/2026):
- compara as câmeras com valor no relatório com as do registro anterior mais recente do mesmo prefixo;
- mesma quantidade e números diferentes → os valores passam, em ordem crescente, para os números do histórico
  (ex.: 22 → 21). É só uma troca de coluna: nada é criado, apagado ou alterado;
- quantidade diferente → ambíguo: fica como veio no relatório e é listado na Auditoria;
- veículo sem histórico → fica como veio.

06/10: **463 veículos remapeados** (ALFA RODOBUS 142, ALFA RODOBUS SPE 123, NORTE BUSS A2 198; 454 de 22 → 21 e 9 de 21 → 22)
e **91 mantidos como vieram** (NORTE BUSS A2 64, GATO PRETO A1 19, GATO PRETO 6, NORTE BUSS A1 1, VIAÇÃO GRAJAÚ 1).
Lista completa: `data/processed/reconciliacao_cameras.csv/.xlsx`; cada registro guarda a origem em
`cameras_reconciliadas` (ex.: "Câmera 22→21") e o motivo em `reconciliacao` (`cftv_consolidado`).

## Tecnologia (e por quê)

- **Processamento: Python** (pandas + openpyxl). Lê as planilhas originais, interpreta os textos das câmeras, relaciona com
  o formulário de manutenção e calcula antes/depois/recorrência. Gera bases tratadas em `data/processed/` e **JSON compacto**
  em `site/public/data/` (≈ 4 MB no total).
- **Site: Vite + JavaScript puro** (sem framework) + [SheetJS](https://sheetjs.com) para exportar Excel.
  Escolhido por ser o mais simples e leve para um painel 100% estático: não precisa de servidor, carrega rápido
  (~125 KB de JS compactado) e a matriz usa uma virtualização própria (só as linhas visíveis são desenhadas), o que
  permite mostrar os 5.467 prefixos sem travar.
- **Caminho relativo**: o site é compilado com `base: './'`, então funciona em qualquer endereço do GitHub Pages
  (ex.: `https://<usuario>.github.io/analise-cftv-manutencoes/`). Para forçar um caminho absoluto:
  `BASE_PATH=/analise-cftv-manutencoes/ npm run build`.

## Instalação (uma vez)

Requisitos: Python 3.11+ e Node.js 20.19+.

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd site && npm install && cd ..
```

## Ver o painel localmente

```bash
cd site
npm run dev          # desenvolvimento: http://localhost:5173
# ou a versão final:
npm run build && npm run preview     # http://localhost:4173
```

## COMO ATUALIZAR OS DADOS

1. Copie os arquivos novos para `data/raw/` (crie a pasta se não existir):
   - `Relatório CFTV - DD.MM.AAAA.xlsx` (um por dia) e/ou
   - o novo `Revisão_CFTV<data_hora>.xlsx` (se houver mais de um, o **mais recente pelo nome** é usado).
   Os arquivos originais nunca são alterados.
2. Rode o script único de atualização (≈ 1 minuto):
   ```bash
   python scripts/atualizar_dados.py
   ```
   Ele relê tudo, mostra as abas usadas/ignoradas de cada arquivo, regrava `data/processed/` e `site/public/data/`.
   Se chegarem arquivos de datas fora de 01–24/09, o período é ampliado automaticamente (todas as datas do período aparecem; sem arquivo = branco).
3. Confira e publique:
   ```bash
   python -m pytest                   # testes das regras (e teste visual, se o site estiver compilado)
   cd site && npm run build           # compila o site em site/dist
   git add -A && git commit -m "Atualiza dados" && git push   # o GitHub Actions publica sozinho
   ```

Scripts auxiliares: `scripts/validacao_manual.py` (validação por amostragem → `docs/VALIDACAO.md`) e
`scripts/capturar_telas.py` (capturas → `docs/screenshots/`). Ambos exigem `site/dist` compilado e Playwright
(`pip install playwright && playwright install chromium`).

## Publicação (GitHub Pages)

- Repositório público: https://github.com/Leticia-Noxxon/analise-cftv-manutencoes
- Dashboard: https://leticia-noxxon.github.io/analise-cftv-manutencoes/ (publicado em 25/09/2026)
- GitHub Pages configurado com **Source: GitHub Actions**. O workflow `.github/workflows/deploy.yml` compila `site/` e
  publica a cada push na `main` (acompanhe em *Actions → Publicar dashboard (GitHub Pages)*).
- Teste do site publicado (navegador headless, perfil limpo): `python scripts/testar_publicado.py` → capturas
  `docs/screenshots/publicado_*.png`.

## Estrutura

```
REGRAS_PROJETO.md          regras de negócio + decisões da usuária (fonte oficial das regras)
README.md
requirements.txt
data/
  raw/                     planilhas originais (NÃO versionadas; nunca alteradas)
  processed/               bases tratadas CSV/XLSX + checksums dos originais
scripts/
  atualizar_dados.py       script único de atualização
  cftv/                    pipeline (config, leitura_cftv, interpretacao, manutencao, analise, exportar)
  validacao_manual.py      fase 13 (amostragem planilha × processado × painel)
  capturar_telas.py        capturas de tela
  servidor_teste.py        servidor local usado pelos testes
  diagnostico/             scripts do diagnóstico inicial (fases 1–4)
site/                      dashboard (Vite)
  public/data/             cftv.json, manutencoes.json, meta.json (gerados)
  src/                     main, matrix, panels, tabs, filters, export, data, util, style
tests/                     pytest: regras obrigatórias (§45) + teste visual
docs/                      especificação, diagnóstico, validação, capturas de tela
.github/workflows/         publicação no GitHub Pages
```

## Dados públicos

A usuária autorizou a publicação dos dados completos. **Ficam públicos** (no site e no repositório):

- **CFTV** (`site/public/data/cftv.json`, `data/processed/cftv_consolidado.xlsx`): prefixo, empresa, data, texto e
  interpretação de cada câmera 21–26, coluna Status (status operacional), coluna Manutenção do CFTV, última transmissão,
  nome do arquivo e linha de origem.
- **Manutenções** (`site/public/data/manutencoes.json`, `data/processed/manutencoes_tratadas.*`, `manutencao_x_cftv.*`,
  `analise_antes_depois.*`, `recorrencias.*`): prefixo, **nome do técnico**, data/hora, ID do formulário, garagem,
  tecnologia do veículo, todas as respostas (problemas, ações, quantidades de câmera/switch/cartão), **observação
  integral do técnico**, **números de série e MACs**, alertas e resultados calculados.
- **Metadados e documentação**: `meta.json` (arquivos/abas, inconsistências), `resumo_arquivos.csv`, `inconsistencias.csv`,
  `docs/` (inclui trechos dos formulários no diagnóstico) e as capturas de tela.

**Não ficam públicos:** as planilhas originais `data/raw/*.xlsx` (não são necessárias para o site), o CSV consolidado de
37 MB (regenerável), arquivos intermediários, `node_modules`, ambientes virtuais, `.env*` e qualquer chave ou token
(o projeto não usa nenhum segredo).

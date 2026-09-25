import './style.css';
import { carregar } from './data.js';
import { FILTROS_PADRAO, aplicar, htmlFiltros, ligarFiltros } from './filters.js';
import { criarMatriz } from './matrix.js';
import { initPaineis, abrirCelula, abrirManutencao, abrirPrefixo } from './panels.js';
import { htmlManutencoes, htmlEfetividade, htmlRecorrencias, htmlAuditoria, htmlComoLer, htmlTaxa } from './tabs.js';
import { exportar, NOMES_PLANILHAS } from './export.js';
import { esc, dmy, fmtN, statusChip, CAMS, camLabel, STATUS } from './util.js';

const ABAS = [
  ['matriz', 'Matriz'], ['manutencoes', 'Manutenções'], ['efetividade', 'Efetividade'],
  ['recorrencias', 'Recorrências'], ['auditoria', 'Auditoria'], ['como-ler', 'Como ler'],
];
const app = document.getElementById('app');
const f = { ...FILTROS_PADRAO, _mais: false };
let D; let aba = 'matriz'; let matriz = null; let L = []; let E = [];

function eventosFiltrados(lista) {
  return lista.flatMap((p) => p.ev).filter((e) => (!f.tecnico || e.tecnicos.includes(f.tecnico))
    && (!f.garagem || e.garagens.includes(f.garagem))
    && (!f.resultado || (f.resultado === 'PENDENCIA' ? e.pendencia : f.resultado === 'NORMAL_ANTES' ? e.veiculo_normal_antes : e.resultado === f.resultado)));
}

function descreverFiltros() {
  const t = [`Veículos: ${{ com: 'com manutenção', todos: 'todos', sem: 'sem manutenção' }[f.veiculos]}`];
  if (f.busca) t.push(`prefixo contém "${f.busca}"`);
  if (f.empresa !== '') t.push(`empresa ${D.cftv.empresas[f.empresa]}`);
  if (f.garagem) t.push(`garagem ${f.garagem}`);
  if (f.tecnico) t.push(`técnico ${f.tecnico}`);
  if (f.camera) t.push(`câmera com problema ${camLabel(+f.camera)}`);
  if (f.situacao) t.push(`situação ${f.situacao}`);
  if (f.status !== '') t.push(`status ${STATUS[f.status].nome}`);
  if (f.data !== '') t.push(`data ${D.cftv.colunas[f.data].rotulo}`);
  if (f.statusOp !== '') t.push(`status operacional ${D.cftv.statusOp[f.statusOp]}`);
  if (f.resultado) t.push(`resultado ${f.resultado}`);
  return t.join('; ');
}

const kpi = (t, v, sub = '', cls = '') => `<div class="kpi ${cls}"><div class="kpi-t">${t}</div><div class="kpi-v">${v}</div>${sub ? `<div class="kpi-s">${sub}</div>` : ''}</div>`;

function htmlKpisMatriz() {
  const comReg = L.filter((p) => p.recs);
  const cams = L.reduce((a, p) => a + p.camsExist.size, 0);
  const nOff = L.filter((p) => p.hasOff).length; const nErr = L.filter((p) => p.hasErr).length;
  const nForms = E.reduce((a, e) => a + e.qtd_formularios, 0);
  return `<div class="kpis kpis-top">
    ${kpi('Veículos analisados', fmtN(comReg.length), L.length !== comReg.length ? `${fmtN(L.length - comReg.length)} sem registro CFTV` : 'com registro CFTV')}
    ${kpi('Câmeras analisadas', fmtN(cams), 'câmeras instaladas (sem “-”)')}
    ${kpi('Com câmera OFFLINE', fmtN(nOff), 'em algum dia do período', 'k-no')}
    ${kpi('Com câmera com erro', fmtN(nErr), 'SD, Login ou Gravação', 'k-par')}
    ${kpi('Manutenções realizadas', fmtN(nForms), `${fmtN(E.length)} eventos (prefixo + data)`, 'k-m')}
    ${kpi('Veículos com manutenção', fmtN(new Set(E.map((e) => e.prefixo)).size), '')}
    ${htmlTaxa(E)}
  </div>`;
}

const legenda = () => `<div class="legend" aria-label="Legenda">
  ${statusChip('V', 'Todas ONLINE sem erro')} ${statusChip('L', 'Câmera ONLINE com erro')} ${statusChip('R', 'Câmera OFFLINE')} ${statusChip(' ', 'Sem dados')}
  <span class="lg-i"><span class="dot-mini"></span> Manutenção (número = mais de um formulário)</span>
  <span class="lg-i muted">Cabeçalho cinza = dia sem arquivo CFTV · Clique: quadrado = detalhes do dia · bolinha = manutenção · prefixo = linha do tempo</span></div>`;

function renderShell() {
  app.innerHTML = `
  <header class="top">
    <div class="brand"><div class="logo">CFTV</div><div><h1>Análise CFTV × Manutenções</h1>
      <div class="sub">Período do CFTV: ${dmy(D.meta.periodo.inicio)} a ${dmy(D.meta.periodo.fim)} · ${fmtN(D.meta.totais.prefixos_cftv)} veículos · ${fmtN(D.meta.totais.formularios)} formulários de manutenção · dados gerados em ${esc(D.meta.gerado_em)}</div></div></div>
    <div class="exp"><button class="btn" id="btn-exp">⬇ Exportar Excel</button>
      <select id="sel-csv" aria-label="Exportar CSV"><option value="">CSV…</option>${NOMES_PLANILHAS.map((n) => `<option>${n}</option>`).join('')}</select></div>
  </header>
  <nav class="tabs" role="tablist">${ABAS.map(([id, t]) => `<button role="tab" data-tab="${id}" class="${aba === id ? 'on' : ''}">${t}</button>`).join('')}</nav>
  <main><div id="filtros"></div><div id="conteudo"></div></main>`;
  app.querySelectorAll('[data-tab]').forEach((b) => b.addEventListener('click', () => { location.hash = b.dataset.tab; }));
  app.querySelector('#btn-exp').addEventListener('click', () => exportar(D, L, E, descreverFiltros(), 'xlsx'));
  app.querySelector('#sel-csv').addEventListener('change', (e) => { if (e.target.value) exportar(D, L, E, descreverFiltros(), e.target.value); e.target.value = ''; });
}

function renderFiltros() {
  const host = app.querySelector('#filtros');
  const usa = !['auditoria', 'como-ler'].includes(aba);
  host.hidden = !usa;
  if (!usa) return;
  host.innerHTML = htmlFiltros(D, f) + `<div class="count muted small" id="f-count"></div>`;
  ligarFiltros(host, f, (rerender) => { if (rerender) renderFiltros(); atualizar(); });
}

function atualizar() {
  L = aplicar(D, f);
  E = eventosFiltrados(L);
  const cnt = app.querySelector('#f-count');
  if (cnt) cnt.textContent = `${fmtN(L.length)} veículo(s) · ${fmtN(E.length)} manutenção(ões) (eventos) com os filtros atuais`;
  const c = app.querySelector('#conteudo');
  if (aba === 'matriz') {
    if (!matriz) {
      c.innerHTML = `<div id="kpis"></div>${legenda()}<div id="matriz" class="matrix"></div>`;
      matriz = criarMatriz(D, c.querySelector('#matriz'), {
        onCelula: (p, j) => abrirCelula(p, j),
        onManutencao: (e) => abrirManutencao(e, false),
        onPrefixo: (p) => abrirPrefixo(p, false),
      });
    }
    c.querySelector('#kpis').innerHTML = htmlKpisMatriz();
    matriz.atualizar(L);
    return;
  }
  matriz = null;
  if (aba === 'manutencoes') c.innerHTML = htmlManutencoes(D, E);
  else if (aba === 'efetividade') c.innerHTML = htmlEfetividade(D, E);
  else if (aba === 'recorrencias') c.innerHTML = htmlRecorrencias(D, L, E);
  else if (aba === 'auditoria') c.innerHTML = htmlAuditoria(D);
  else c.innerHTML = htmlComoLer(D);
}

function irPara() {
  const h = location.hash.replace('#', '');
  aba = ABAS.some(([id]) => id === h) ? h : 'matriz';
  app.querySelectorAll('[data-tab]').forEach((b) => b.classList.toggle('on', b.dataset.tab === aba));
  matriz = null;
  renderFiltros();
  atualizar();
}

async function iniciar() {
  app.innerHTML = '<div class="loading">Carregando dados…</div>';
  try {
    D = await carregar();
  } catch (err) {
    app.innerHTML = `<div class="loading err">Não foi possível carregar os dados: ${esc(err.message)}</div>`;
    return;
  }
  window.__D = D; // usado pelos testes automatizados
  initPaineis(D);
  renderShell();
  app.querySelector('#conteudo').addEventListener('click', (e) => {
    const tr = e.target.closest('tr[data-ev]');
    if (tr) { abrirManutencao(D.eventos[+tr.dataset.ev], false); return; }
    const tp = e.target.closest('tr[data-p]');
    if (tp) abrirPrefixo(D.byPrefixo[+tp.dataset.p], false);
  });
  window.addEventListener('hashchange', irPara);
  irPara();
  document.body.dataset.pronto = '1';
}
iniciar();

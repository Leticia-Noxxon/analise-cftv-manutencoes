// Painéis laterais: detalhe da célula (§10), manutenção (§17) e linha do tempo do prefixo (§23).
import { esc, camLabel, camInfo, camExiste, CAMS, dm, dmy, STATUS, statusChip, resBadge, POS } from './util.js';
import { registroDoDia } from './data.js';

let D;
const drawer = () => document.getElementById('drawer');
const backdrop = () => document.getElementById('drawer-backdrop');
const pilha = [];

export function initPaineis(dados) {
  D = dados;
  backdrop().addEventListener('click', fechar);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') fechar(); });
  drawer().addEventListener('click', (e) => {
    const a = e.target.closest('[data-act]');
    if (!a) return;
    const { act } = a.dataset;
    if (act === 'fechar') fechar();
    else if (act === 'voltar') voltar();
    else if (act === 'manut') abrirManutencao(D.eventos[+a.dataset.ev]);
    else if (act === 'prefixo') abrirPrefixo(D.byPrefixo[+a.dataset.p]);
    else if (act === 'celula') abrirCelula(D.byPrefixo[+a.dataset.p], +a.dataset.j);
    else if (act === 'form') {
      drawer().querySelectorAll('.form-tab').forEach((b) => b.classList.toggle('on', b === a));
      drawer().querySelectorAll('.form-body').forEach((b) => { b.hidden = b.dataset.f !== a.dataset.f; });
    }
  });
}

function abrir(html, largo = false, empilhar = true) {
  const d = drawer();
  if (empilhar && !d.hidden) pilha.push({ html: d.innerHTML, largo: d.classList.contains('wide') });
  if (!empilhar) pilha.length = 0;
  d.classList.toggle('wide', largo);
  d.innerHTML = `<div class="dr-top">${pilha.length ? '<button class="btn-ghost" data-act="voltar">← Voltar</button>' : '<span></span>'}<button class="btn-ghost" data-act="fechar" aria-label="Fechar">✕ Fechar</button></div><div class="dr-body">${html}</div>`;
  d.hidden = false; backdrop().hidden = false;
  d.querySelector('.dr-body').scrollTop = 0;
}
function voltar() {
  const prev = pilha.pop();
  if (!prev) return fechar();
  const d = drawer();
  d.classList.toggle('wide', prev.largo);
  d.innerHTML = prev.html;
  if (!pilha.length) d.querySelector('[data-act="voltar"]')?.replaceWith(document.createElement('span'));
}
export function fechar() { drawer().hidden = true; backdrop().hidden = true; pilha.length = 0; }

const kv = (k, v) => (v == null || v === '' ? '' : `<div class="kv"><span>${esc(k)}</span><b>${v}</b></div>`);
const sec = (t, body) => (body ? `<section class="sec"><h4>${esc(t)}</h4>${body}</section>` : '');

// ---------------------------------------------------------------- CÉLULA
export function abrirCelula(p, j, empilhar = false) {
  const col = D.cftv.colunas[j];
  const rec = registroDoDia(D, p, j);
  const evs = p.evByCol[j] || [];
  let h = `<div class="dr-title"><small>DETALHE DO DIA</small><h2>Prefixo ${p.p} · ${dmy(col.data)}</h2></div>`;
  if (!rec) {
    h += `<div class="big-status sB">SEM DADOS — ${col.fora_periodo ? `data fora do período do CFTV (${dm(D.meta.periodo.inicio)} a ${dm(D.meta.periodo.fim)})` : (col.tem_arquivo ? (p.e >= 0 && !D.empresasPorCol[j].has(p.e) ? `a empresa ${esc(p.empresa)} não consta no arquivo desta data` : 'o veículo não aparece no arquivo desta data') : 'não há arquivo CFTV nesta data')}</div>
      <p class="muted">Ausência de registro não é considerada OFFLINE nem erro.</p>`;
  } else {
    h += `<div class="big-status ${STATUS[rec.status].cls}">${STATUS[rec.status].nome} — ${STATUS[rec.status].desc}</div>`;
    h += `<div class="kvs">${kv('Empresa (CFTV)', esc(rec.empresa))}${kv('Garagem (manutenção)', esc([...p.garagens].join(', ')))}${kv('Status operacional (CFTV)', esc(rec.statusOp))}${kv('Última manutenção segundo o CFTV', esc(rec.manutCftv === '#N/A' ? '#N/A (sem registro)' : rec.manutCftv ? dmy(rec.manutCftv) : ''))}</div>`;
    const cams = rec.cams.filter((c) => camExiste(c.code));
    h += sec('Câmeras', `<table class="tbl"><thead><tr><th>Câmera</th><th>Status</th><th>SD</th><th>Login</th><th>Gravação</th></tr></thead><tbody>
      ${cams.map((c) => { const i = camInfo(c.code); const v = (x) => (x ? `<span class="${x === 'error' ? 'err' : 'ok'}">${x}</span>` : '<span class="muted">—</span>'); return `<tr><td>${camLabel(c.n)}</td><td><span class="sq ${i.cls}"></span>${i.texto}</td><td>${v(i.sd)}</td><td>${v(i.login)}</td><td>${v(i.grav)}</td></tr>`; }).join('')}
      </tbody></table>`);
    h += `<p class="origem">Origem: ${esc(rec.arquivo)} · aba "${esc(rec.arquivo?.replace('.xlsx', ''))}" · linha ${rec.linha}</p>`;
  }
  if (evs.length) {
    h += sec('Manutenção neste dia', evs.map((e) => cardEvento(e)).join(''));
  }
  h += `<div class="actions"><button class="btn" data-act="prefixo" data-p="${p.p}">Ver linha do tempo do prefixo ${p.p}</button></div>`;
  abrir(h, false, empilhar);
}

function cardEvento(e) {
  return `<div class="ev-card"><div><b>${dm(e.data)} ${esc(e.horas.join(', '))}</b> · ${esc(e.tecnicos.join(', '))}${e.qtd_formularios > 1 ? ` · <span class="dot-mini"></span> ${e.qtd_formularios} formulários` : ''}</div>
    <div class="ev-res">${resBadge(e.resultado)} ${e.pendencia ? '<span class="flag fPend">Pendência</span>' : ''} ${e.veiculo_normal_antes ? '<span class="flag fInfo">Já estava normal antes</span>' : ''}</div>
    <button class="btn-link" data-act="manut" data-ev="${e.idx}">Ver manutenção completa →</button></div>`;
}

// ---------------------------------------------------------------- MANUTENÇÃO
function passos(e) {
  const a = e.antes; const d0 = e.dia; const dep = e.depois;
  const n = e.normalizacao;
  const probl = (r) => (r && r.problemas.length ? r.problemas.map((x) => `${esc(x.rotulo)} <b>${esc(x.descricao)}</b>`).join('<br>') : '');
  const depTxt = !dep.length ? '<span class="muted">Sem registro posterior</span>'
    : `${dep.slice(0, 8).map((r) => `<span class="mini ${STATUS[r.status].cls}" title="${dm(r.data)} ${r.status_nome}">${dm(r.data).slice(0, 2)}</span>`).join('')}${dep.length > 8 ? '…' : ''}
       <div class="small">${n?.normalizou ? `Normalizou em ${dm(n.primeiro_normal)} (${n.registros_ate_normalizar}º registro)` : (n ? 'Não normalizou por completo' : '')}</div>`;
  const recTxt = e.recorrencia ? `<b class="t-red">SIM</b> — ${dm(e.recorrencia.data)}<br>${e.recorrencia.problemas.map((x) => esc(x.rotulo)).join(', ')} (mesma câmera)`
    : (n?.normalizou ? '<b class="t-green">NÃO</b> voltou' : '<span class="muted">—</span>');
  return `<div class="steps">
    <div class="step"><small>ANTES</small>${a ? `<div>${statusChip(a.status, dm(a.data))}</div><div class="small">${probl(a) || 'Todas ONLINE sem erro'}</div>` : '<span class="muted">Sem registro anterior</span>'}</div>
    <div class="arrow">→</div>
    <div class="step st-m"><small>MANUTENÇÃO</small><div><span class="dot-mini"></span> <b>${dm(e.data)}</b> ${esc(e.horas.join(', '))}</div><div class="small">${esc(e.tecnicos.join(', '))}</div>
      <div class="small muted">No dia: ${d0 ? statusChip(d0.status) : 'sem registro'}</div></div>
    <div class="arrow">→</div>
    <div class="step"><small>DEPOIS</small>${depTxt}</div>
    <div class="arrow">→</div>
    <div class="step"><small>O PROBLEMA VOLTOU?</small><div class="small">${recTxt}</div></div>
  </div>`;
}

function blocoResultado(e) {
  return `<div class="res-box">
    <div class="res-line"><span>Resultado:</span> ${resBadge(e.resultado)}</div>
    <div class="small">${esc(e.motivo || '')}</div>
    ${e.veiculo_normal_antes ? '<div class="flag-big fInfo">ℹ️ Veículo já estava normal antes da manutenção (o CFTV não mostrava problema no último registro anterior).</div>' : ''}
    ${e.pendencia ? `<div class="flag-big fPend">⚠️ Pendência registrada pelo técnico:<ul>${e.pendencia_trechos.map((t) => `<li>${esc(t.trecho)} <span class="muted">(termo: “${esc(t.termo)}”)</span></li>`).join('')}</ul></div>` : ''}
  </div>`;
}

export function abrirManutencao(e, empilhar = true) {
  const p = D.byPrefixo[e.prefixo];
  let h = `<div class="dr-title"><small>MANUTENÇÃO</small><h2>Prefixo ${e.prefixo} · ${dmy(e.data)}</h2></div>`;
  h += blocoResultado(e) + passos(e);
  h += sec('O que aconteceu (em frases)', `<ol class="story">${e.historia.map((s) => `<li>${esc(s)}</li>`).join('')}</ol>`);
  const fs = e.formsObj;
  if (fs.length > 1) h += `<div class="form-tabs">${fs.map((f, i) => `<button class="form-tab ${i ? '' : 'on'}" data-act="form" data-f="${i}">Formulário ${i + 1} · ${esc(f.hora)}</button>`).join('')}</div>`;
  fs.forEach((f, i) => { h += `<div class="form-body" data-f="${i}" ${i ? 'hidden' : ''}>${htmlFormulario(f, p)}</div>`; });
  h += `<div class="actions">${p ? `<button class="btn" data-act="prefixo" data-p="${e.prefixo}">Ver linha do tempo do prefixo</button>` : ''}
        ${p && e.col != null ? `<button class="btn-ghost" data-act="celula" data-p="${e.prefixo}" data-j="${e.col}">Ver CFTV do dia</button>` : ''}</div>`;
  abrir(h, true, empilhar);
}

function htmlFormulario(f, p) {
  const anom = f.posicoes.filter((x) => x.anomalias.length);
  const acoes = f.posicoes.filter((x) => x.acoes_realizadas.length);
  const semAnom = f.posicoes.filter((x) => !x.anomalias.length).map((x) => x.rotulo);
  const semAcao = f.posicoes.filter((x) => !x.acoes_realizadas.length && x.acoes.length).map((x) => x.rotulo);
  const eq = f.equipamento;
  const eqHtml = (k) => { const x = eq[k]; return x.series.length || x.macs.length ? `${x.series.length ? kv('Número de série', esc(x.series.join(', '))) : ''}${x.macs.length ? kv('MAC', esc(x.macs.join(', '))) : ''}` : ''; };
  const q = Object.entries(f.quantidades).filter(([, v]) => v != null);
  let h = sec('Manutenção', `<div class="kvs">${kv('Prefixo', f.prefixo)}${kv('Data', dmy(f.data))}${kv('Hora', esc(f.hora))}${kv('Técnico', esc(f.tecnico) + (f.tecnico !== f.tecnico_original ? ` <span class="muted">(no formulário: “${esc(f.tecnico_original)}”)</span>` : ''))}
    ${kv('Empresa (CFTV)', esc(p ? p.empresa : '—'))}${kv('Garagem', esc(f.garagem))}${kv('Tecnologia do veículo', esc(f.tecnologia))}${kv('ID (formulário)', esc(f.id_formulario))}</div>`);
  h += sec('Anomalias encontradas', anom.length ? anom.map((x) => `<div class="pos"><b>${esc(x.rotulo)}</b><div>${x.anomalias.map((a) => `<span class="tag">${esc(a)}</span>`).join('')}</div></div>`).join('')
    + (semAnom.length ? `<div class="small muted">Sem anomalia: ${esc(semAnom.join(', '))}</div>` : '') : '<div class="muted">Nenhuma anomalia marcada nas colunas do formulário.</div>');
  const citadas = f.cameras_citadas_texto.map((n) => `Camera ${n} → <b>${esc(camLabel(n))}</b>`);
  h += sec('Câmeras mencionadas', `${anom.length ? `<div>Com anomalia no formulário: <b>${esc(anom.map((x) => x.rotulo).join(', '))}</b></div>` : ''}
    ${citadas.length ? `<div>Câmera informada pelo técnico no texto: ${citadas.join('; ')}</div>` : ''}
    ${f.notacao_c_texto.length ? `<div>Notação informada pelo técnico: <b>${esc(f.notacao_c_texto.join(', '))}</b> <span class="muted">(não convertida para número de câmera — sem correspondência confirmada)</span></div>` : ''}
    ${!anom.length && !citadas.length && !f.notacao_c_texto.length ? '<div class="muted">Nenhuma câmera mencionada.</div>' : ''}`);
  h += sec('Ações realizadas', acoes.length ? acoes.map((x) => `<div class="pos"><b>${esc(x.rotulo)}</b><div>${x.acoes_realizadas.map((a) => `<span class="tag tag-a">${esc(a)}</span>`).join('')}</div></div>`).join('')
    + (semAcao.length ? `<div class="small muted">Nenhuma ação realizada: ${esc(semAcao.join(', '))}</div>` : '') : '<div class="muted">Nenhuma ação marcada nas colunas do formulário.</div>');
  h += sec('Peças / equipamentos', (f.pecas.length ? `<ul>${f.pecas.map((x) => `<li>${esc(x)}</li>`).join('')}</ul>` : '') + (q.length ? `<div class="kvs">${q.map(([k, v]) => kv(k, esc(v))).join('')}</div>` : ''));
  h += sec('Equipamento instalado', eqHtml('instalado'));
  h += sec('Equipamento retirado', eqHtml('retirado'));
  h += sec('Número de série / MAC (sem indicação de instalado/retirado)', eqHtml('nao_especificado'));
  h += sec('Pendências', f.pendencia_trechos.map((t) => `<div class="pend">${esc(t.trecho)} <span class="muted">(${esc(t.origem)}; termo: “${esc(t.termo)}”)</span></div>`).join(''));
  h += sec('Observação completa do técnico', f.observacoes ? `<div class="obs">${esc(f.observacoes)}</div>` : '<div class="muted">Sem observação.</div>');
  h += sec('Demais respostas do formulário (todas as colunas preenchidas)', `<table class="tbl tbl-kv"><tbody>${f.respostas.map((r) => `<tr><th>${esc(r.coluna)}</th><td class="pre">${esc(r.valor)}</td></tr>`).join('')}</tbody></table>`);
  if (f.alertas.length) h += sec('Alertas de dados', `<ul class="alerts">${f.alertas.map((a) => `<li>${esc(a)}</li>`).join('')}</ul>`);
  h += `<p class="origem">Origem: ${esc(f.arquivo_origem)} · aba Sheet1 · linha ${f.linha_excel}</p>`;
  return h;
}

// ---------------------------------------------------------------- LINHA DO TEMPO
function eventosDoPrefixo(p) {
  const cols = D.cftv.colunas;
  const itens = [];
  CAMS.forEach((n, c) => {
    let prev = null; let jaFalhou = false;
    for (let j = 0; j < cols.length; j++) {
      if (p.g[j] === ' ') continue;
      const code = p.k[j * 6 + c];
      if (!camExiste(code) || code === '?') continue;
      const inf = camInfo(code);
      const st = inf.tipo;
      const err = inf.erros.length ? ` (${inf.erros.join(', ')})` : '';
      if (prev === null) {
        if (st !== 'N') { itens.push({ j, tipo: st, txt: `${camLabel(n)} já estava ${inf.texto}${err} no primeiro registro disponível` }); jaFalhou = true; }
      } else if (st !== prev) {
        if (st === 'N') itens.push({ j, tipo: 'N', txt: `${camLabel(n)} voltou ONLINE normal` });
        else if (st === 'O') { itens.push({ j, tipo: 'O', txt: `${camLabel(n)} ficou OFFLINE${jaFalhou ? ' novamente' : ''}` }); jaFalhou = true; }
        else if (st === 'E') { itens.push({ j, tipo: 'E', txt: prev === 'O' ? `${camLabel(n)} voltou ONLINE, mas com erro${err}` : `${camLabel(n)} ficou ONLINE COM ERRO${err}${jaFalhou ? ' novamente' : ''}` }); jaFalhou = true; }
      }
      prev = st;
    }
  });
  p.ev.forEach((e) => {
    const acoes = [...new Set(e.formsObj.flatMap((f) => f.posicoes.flatMap((x) => x.acoes_realizadas.map((a) => `${a} (${x.posicao})`))))];
    itens.push({ j: e.col ?? 999, tipo: 'M', ev: e, txt: `MANUTENÇÃO — ${e.tecnicos.join(', ')} às ${e.horas.join(', ')}${acoes.length ? `. Intervenção: ${acoes.slice(0, 4).join('; ')}${acoes.length > 4 ? '…' : ''}` : ''}` });
  });
  itens.sort((a, b) => a.j - b.j || (a.tipo === 'M' ? 1 : 0) - (b.tipo === 'M' ? 1 : 0));
  return itens;
}

export function abrirPrefixo(p, empilhar = true) {
  const cols = D.cftv.colunas;
  let h = `<div class="dr-title"><small>LINHA DO TEMPO</small><h2>Prefixo ${p.p}</h2><div class="muted">${esc(p.empresa)}${p.garagens.size ? ` · Garagem: ${esc([...p.garagens].join(', '))}` : ''}${p.semCftv ? ' · este prefixo não aparece em nenhum Relatório CFTV' : ''}</div></div>`;
  h += `<div class="strip">${cols.map((c, j) => `<button class="sd ${STATUS[p.g[j]].cls} ${c.fora_periodo ? 'fora' : ''}" data-act="celula" data-p="${p.p}" data-j="${j}" title="${c.rotulo}: ${STATUS[p.g[j]].nome}${p.evByCol[j] ? ' + manutenção' : ''}">
      <span class="sd-d">${c.rotulo.slice(0, 2)}</span>${p.evByCol[j] ? '<span class="dot-mini"></span>' : ''}</button>`).join('')}</div>
    <div class="strip-legend small muted">Cada quadrado é um dia (${dm(D.meta.periodo.inicio)} a ${dm(D.meta.periodo.fim)}${cols.some((c) => c.fora_periodo) ? ' + manutenções fora do período' : ''}). Clique em um dia para ver as câmeras.</div>`;
  h += `<div class="resumo-dias">${statusChip('V', `${p.nV} dia(s) verde(s)`)} ${statusChip('L', `${p.nL} laranja(s)`)} ${statusChip('R', `${p.nR} vermelho(s)`)} ${statusChip(' ', `${cols.filter((c) => !c.fora_periodo).length - p.recs} sem dados`)}
     <span class="muted">· Câmeras do veículo: ${[...p.camsExist].sort().map((n) => esc(camLabel(n))).join(', ') || '—'}</span></div>`;
  if (p.ev.length) {
    h += `<h3 class="h3">Manutenções: antes → depois</h3>`;
    p.ev.forEach((e) => {
      h += `<div class="ev-story">${blocoResultado(e)}${passos(e)}<ol class="story">${e.historia.map((s) => `<li>${esc(s)}</li>`).join('')}</ol>
        <button class="btn-link" data-act="manut" data-ev="${e.idx}">Ver manutenção completa (anomalias, ações, observação do técnico) →</button></div>`;
    });
  } else {
    h += '<p class="muted">Este veículo não recebeu manutenção no formulário.</p>';
  }
  const itens = eventosDoPrefixo(p);
  h += `<h3 class="h3">Eventos do período</h3>`;
  h += itens.length ? `<ul class="events">${itens.map((it) => `<li class="evt ev-${it.tipo}"><span class="evt-d">${it.j === 999 ? '—' : dm(cols[it.j].data)}</span><span class="evt-i"></span><span>${esc(it.txt)}${it.ev ? ` → ${resBadge(it.ev.resultado)}` : ''}</span></li>`).join('')}</ul>`
    : '<p class="muted">Nenhuma mudança: todas as câmeras permaneceram ONLINE normais nos registros disponíveis.</p>';
  abrir(h, true, empilhar);
}

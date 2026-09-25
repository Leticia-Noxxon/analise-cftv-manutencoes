// Matriz/heatmap virtualizada: só as linhas visíveis são desenhadas (suporta os 5.429 prefixos sem travar).
import { esc, camLabel, camInfo, camExiste, dm, STATUS, statusChip } from './util.js';
import { registroDoDia } from './data.js';

const ROW_H = 30;
const HEAD_H = 46;
const FIRST_W = 178;
const CELL_W = 34;

export function criarMatriz(D, host, handlers) {
  const cols = D.cftv.colunas;
  let lista = [];
  host.innerHTML = `
    <div class="mx-scroll" tabindex="0" aria-label="Matriz de prefixos por data">
      <div class="mx-inner">
        <div class="mx-head" style="height:${HEAD_H}px">
          <div class="mx-corner" style="width:${FIRST_W}px">Prefixo <span class="muted">· empresa</span></div>
          ${cols.map((c, j) => `<div class="mx-h ${c.tem_arquivo ? '' : 'nofile'} ${c.fora_periodo ? 'fora' : ''}" style="width:${CELL_W}px" data-j="${j}"
              title="${esc(c.fora_periodo ? `${c.rotulo}: fora do período do CFTV (só manutenções)` : (c.tem_arquivo ? `${c.rotulo}: ${c.arquivo}` : `${c.rotulo}: não há arquivo CFTV nesta data`))}">
              <b>${c.rotulo.slice(0, 2)}</b><small>${c.fora_periodo ? 'fora' : c.dia_semana}</small></div>`).join('')}
        </div>
        <div class="mx-rows"></div>
      </div>
      <div class="mx-empty" hidden>Nenhum veículo encontrado com estes filtros.</div>
    </div>`;
  const scroll = host.querySelector('.mx-scroll');
  const inner = host.querySelector('.mx-inner');
  const rows = host.querySelector('.mx-rows');
  const empty = host.querySelector('.mx-empty');
  const tip = document.getElementById('tooltip');
  inner.style.width = `${FIRST_W + cols.length * CELL_W + 8}px`;

  let raf = 0;
  function desenhar() {
    raf = 0;
    const top = scroll.scrollTop;
    const h = scroll.clientHeight || 600;
    const i0 = Math.max(0, Math.floor((top - HEAD_H) / ROW_H) - 6);
    const i1 = Math.min(lista.length, Math.ceil((top + h) / ROW_H) + 6);
    let html = '';
    for (let i = i0; i < i1; i++) {
      const p = lista[i];
      let cells = '';
      for (let j = 0; j < cols.length; j++) {
        const g = p.g[j];
        const evs = p.evByCol[j];
        const nf = evs ? evs.reduce((a, e) => a + e.qtd_formularios, 0) : 0;
        cells += `<div class="c ${STATUS[g].cls}${cols[j].fora_periodo ? ' fora' : ''}" data-i="${i}" data-j="${j}">${evs ? `<span class="dot" data-i="${i}" data-j="${j}" role="button" aria-label="Manutenção">${nf > 1 ? nf : ''}</span>` : ''}</div>`;
      }
      html += `<div class="mx-row" style="top:${HEAD_H + i * ROW_H}px"><div class="pf" data-i="${i}" style="width:${FIRST_W}px" role="button" title="Ver linha do tempo do prefixo ${p.p}">
        <b>${p.p}</b><span>${esc(p.empresa)}</span></div>${cells}</div>`;
    }
    rows.innerHTML = html;
  }
  const agendar = () => { if (!raf) raf = requestAnimationFrame(desenhar); };
  scroll.addEventListener('scroll', () => { agendar(); tip.hidden = true; }, { passive: true });
  new ResizeObserver(agendar).observe(scroll);

  // Tooltip (§9): prefixo, data, status geral e cada câmera
  scroll.addEventListener('mousemove', (e) => {
    const cell = e.target.closest('.c');
    if (!cell) { tip.hidden = true; return; }
    const p = lista[+cell.dataset.i];
    const j = +cell.dataset.j;
    tip.innerHTML = htmlTooltip(D, p, j);
    tip.hidden = false;
    const r = tip.getBoundingClientRect();
    let x = e.clientX + 16; let y = e.clientY + 14;
    if (x + r.width > window.innerWidth - 8) x = e.clientX - r.width - 16;
    if (y + r.height > window.innerHeight - 8) y = window.innerHeight - r.height - 8;
    tip.style.left = `${x}px`; tip.style.top = `${y}px`;
  });
  scroll.addEventListener('mouseleave', () => { tip.hidden = true; });
  scroll.addEventListener('click', (e) => {
    tip.hidden = true;
    const dot = e.target.closest('.dot');
    if (dot) { const p = lista[+dot.dataset.i]; handlers.onManutencao(p.evByCol[+dot.dataset.j][0], p.evByCol[+dot.dataset.j]); return; }
    const c = e.target.closest('.c');
    if (c) { handlers.onCelula(lista[+c.dataset.i], +c.dataset.j); return; }
    const pf = e.target.closest('.pf');
    if (pf) handlers.onPrefixo(lista[+pf.dataset.i]);
  });

  return {
    atualizar(novaLista) {
      lista = novaLista;
      inner.style.height = `${HEAD_H + lista.length * ROW_H + 4}px`;
      empty.hidden = lista.length > 0;
      scroll.scrollTop = 0;
      desenhar();
    },
  };
}

export function htmlTooltip(D, p, j) {
  const col = D.cftv.colunas[j];
  const rec = registroDoDia(D, p, j);
  const evs = p.evByCol[j];
  let h = `<div class="tt-h"><b>Prefixo ${p.p}</b> · ${dm(col.data)}${col.fora_periodo ? ' (fora do período CFTV)' : ''}</div>`;
  if (!rec) {
    h += `<div class="tt-s">${statusChip(' ')} <span class="muted">${col.fora_periodo ? 'Fora do período do CFTV' : col.tem_arquivo ? (p.e >= 0 && !D.empresasPorCol[j].has(p.e) ? `A empresa ${esc(p.empresa)} não consta no arquivo desta data` : 'Veículo sem registro no arquivo desta data') : 'Não há arquivo CFTV nesta data'}</span></div>`;
  } else {
    h += `<div class="tt-s">Status geral: ${statusChip(rec.status)}</div><ul class="tt-cams">`;
    rec.cams.filter((c) => camExiste(c.code)).forEach((c) => {
      const inf = camInfo(c.code);
      h += `<li><span class="sq ${inf.cls}"></span>${camLabel(c.n)} — <b>${inf.texto}</b>${inf.erros.length ? ` <span class="muted">/ ${inf.erros.map((x) => `${x}: error`).join(' / ')}</span>` : ''}</li>`;
    });
    h += '</ul>';
    if (rec.statusOp) h += `<div class="tt-f">Status operacional (CFTV): <b>${esc(rec.statusOp)}</b></div>`;
  }
  if (evs) {
    const nf = evs.reduce((a, e) => a + e.qtd_formularios, 0);
    h += `<div class="tt-m"><span class="dot-mini"></span> Manutenção neste dia (${nf} formulário${nf > 1 ? 's' : ''}) — ${esc(evs[0].tecnicos.join(', '))}. Clique na bolinha para ver.</div>`;
  }
  h += '<div class="tt-f muted">Clique na célula para detalhes</div>';
  return h;
}

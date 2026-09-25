// Filtros (aplicados a todas as abas de análise)
import { esc, camLabel, CAMS, RESULTADOS, STATUS } from './util.js';

export const FILTROS_PADRAO = { veiculos: 'com', busca: '', empresa: '', garagem: '', tecnico: '', camera: '', situacao: '', status: '', data: '', statusOp: '', resultado: '', ordem: 'prefixo' };

export function aplicar(D, f) {
  const busca = f.busca.trim();
  const j = f.data !== '' ? Number(f.data) : null;
  const out = D.P.filter((p) => {
    if (f.veiculos === 'com' && !p.ev.length) return false;
    if (f.veiculos === 'sem' && p.ev.length) return false;
    if (busca && !String(p.p).includes(busca)) return false;
    if (f.empresa !== '' && !p.empresasIdx.has(Number(f.empresa))) return false;
    if (f.garagem && !p.garagens.has(f.garagem)) return false;
    if (f.tecnico && !p.tecnicos.has(f.tecnico)) return false;
    if (f.camera && !p.camsProb.has(Number(f.camera))) return false;
    if (f.situacao === 'off' && !p.hasOff) return false;
    if (f.situacao === 'err' && !p.hasErr) return false;
    if (f.situacao === 'normal' && !p.allNormal) return false;
    if (f.status !== '') {
      if (j != null) { if (p.g[j] !== f.status) return false; } else if (!p.g.includes(f.status)) return false;
    } else if (j != null && p.g[j] === ' ' && !p.evByCol[j]) return false;
    if (f.statusOp !== '' && !p.sops.has(Number(f.statusOp))) return false;
    if (f.resultado) {
      if (f.resultado === 'PENDENCIA') { if (!p.pend) return false; }
      else if (f.resultado === 'NORMAL_ANTES') { if (!p.normalAntes) return false; }
      else if (!p.resultados.has(f.resultado)) return false;
    }
    return true;
  });
  if (f.ordem === 'problema') out.sort((a, b) => b.nR - a.nR || b.probDias - a.probDias || a.p - b.p);
  else if (f.ordem === 'manut') out.sort((a, b) => b.nForms - a.nForms || a.p - b.p);
  return out;
}

const opt = (v, t, sel) => `<option value="${esc(v)}"${String(sel) === String(v) ? ' selected' : ''}>${esc(t)}</option>`;

export function htmlFiltros(D, f) {
  const cols = D.cftv.colunas;
  const nAtivos = ['empresa', 'garagem', 'tecnico', 'camera', 'situacao', 'status', 'data', 'statusOp', 'resultado'].filter((k) => f[k] !== '').length + (f.busca ? 1 : 0);
  return `
  <div class="filters" role="search">
    <div class="frow">
      <input id="f-busca" class="search" type="search" placeholder="Buscar prefixo..." value="${esc(f.busca)}" autocomplete="off" aria-label="Buscar prefixo" />
      <div class="seg" role="group" aria-label="Veículos">
        ${[['com', 'Com manutenção'], ['todos', 'Todos os veículos'], ['sem', 'Sem manutenção']].map(([v, t]) => `<button data-veic="${v}" class="${f.veiculos === v ? 'on' : ''}">${t}</button>`).join('')}
      </div>
      <select id="f-situacao" aria-label="Situação no período">
        ${opt('', 'Situação no período: todas', f.situacao)}${opt('off', 'Teve câmera OFFLINE', f.situacao)}${opt('err', 'Teve câmera com erro', f.situacao)}${opt('normal', '100% normal (sempre verde)', f.situacao)}
      </select>
      <select id="f-resultado" aria-label="Resultado da manutenção">
        ${opt('', 'Resultado da manutenção: todos', f.resultado)}${RESULTADOS.map((r) => opt(r, r, f.resultado)).join('')}
        ${opt('PENDENCIA', 'Com pendência registrada', f.resultado)}${opt('NORMAL_ANTES', 'Veículo já estava normal antes', f.resultado)}
      </select>
      <button id="f-mais" class="btn-link">${f._mais ? 'Menos filtros ▲' : 'Mais filtros ▼'}</button>
      ${nAtivos ? `<button id="f-limpar" class="btn-link">Limpar filtros (${nAtivos})</button>` : ''}
    </div>
    <div class="frow more" ${f._mais ? '' : 'hidden'}>
      <select id="f-empresa" aria-label="Empresa">${opt('', 'Empresa (CFTV): todas', f.empresa)}${D.cftv.empresas.map((e, i) => opt(i, e, f.empresa)).join('')}</select>
      <select id="f-garagem" aria-label="Garagem">${opt('', 'Garagem (manutenção): todas', f.garagem)}${D.garagens.map((g) => opt(g, g, f.garagem)).join('')}</select>
      <select id="f-tecnico" aria-label="Técnico">${opt('', 'Técnico: todos', f.tecnico)}${D.tecnicos.map((t) => opt(t, t, f.tecnico)).join('')}</select>
      <select id="f-camera" aria-label="Câmera com problema">${opt('', 'Câmera com problema: qualquer', f.camera)}${CAMS.map((n) => opt(n, camLabel(n), f.camera)).join('')}</select>
      <select id="f-status" aria-label="Status geral">${opt('', 'Status do dia: qualquer', f.status)}${['V', 'L', 'R', ' '].map((s) => opt(s, `Status: ${STATUS[s].nome}`, f.status)).join('')}</select>
      <select id="f-data" aria-label="Data">${opt('', 'Data: qualquer', f.data)}${cols.map((c, i) => opt(i, `Data: ${c.rotulo}${c.tem_arquivo ? '' : ' (sem arquivo)'}`, f.data)).join('')}</select>
      <select id="f-statusOp" aria-label="Status operacional do CFTV">${opt('', 'Status operacional (CFTV): todos', f.statusOp)}${D.cftv.statusOp.map((s, i) => opt(i, s, f.statusOp)).join('')}</select>
      <select id="f-ordem" aria-label="Ordenar">${opt('prefixo', 'Ordenar: prefixo', f.ordem)}${opt('problema', 'Ordenar: mais dias vermelhos', f.ordem)}${opt('manut', 'Ordenar: mais manutenções', f.ordem)}</select>
    </div>
  </div>`;
}

export function ligarFiltros(root, f, onChange) {
  const q = (s) => root.querySelector(s);
  let t;
  q('#f-busca').addEventListener('input', (e) => { clearTimeout(t); const v = e.target.value; t = setTimeout(() => { f.busca = v; onChange(false); }, 60); });
  root.querySelectorAll('[data-veic]').forEach((b) => b.addEventListener('click', () => { f.veiculos = b.dataset.veic; onChange(true); }));
  ['situacao', 'resultado', 'empresa', 'garagem', 'tecnico', 'camera', 'status', 'data', 'statusOp', 'ordem'].forEach((k) => {
    q(`#f-${k}`).addEventListener('change', (e) => { f[k] = e.target.value; onChange(true); });
  });
  q('#f-mais').addEventListener('click', () => { f._mais = !f._mais; onChange(true); });
  q('#f-limpar')?.addEventListener('click', () => { Object.assign(f, { ...FILTROS_PADRAO, veiculos: f.veiculos, _mais: f._mais }); onChange(true); });
}

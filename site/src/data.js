// Carrega os JSON pré-processados (scripts/atualizar_dados.py) e monta estruturas derivadas para filtros rápidos.
import { CAMS, camExiste, camProblema } from './util.js';

export async function carregar() {
  const base = import.meta.env.BASE_URL;
  const [cftv, man, meta] = await Promise.all(['cftv', 'manutencoes', 'meta'].map((n) => fetch(`${base}data/${n}.json`).then((r) => {
    if (!r.ok) throw new Error(`Falha ao carregar data/${n}.json`);
    return r.json();
  })));
  const D = { cftv, meta, forms: man.forms, eventos: man.eventos };
  D.ncol = cftv.colunas.length;
  D.colIdx = Object.fromEntries(cftv.colunas.map((c, i) => [c.data, i]));
  D.formById = Object.fromEntries(man.forms.map((f) => [f.id_form, f]));
  D.eventos.forEach((e, i) => { e.idx = i; e.col = D.colIdx[e.data]; e.formsObj = e.forms.map((id) => D.formById[id]); });
  // texto original por código (auditoria): só quando o código corresponde a um único texto na base
  const porCodigo = {};
  meta.auditoria_textos.forEach((t) => { (porCodigo[t.codigo] ||= []).push(t.original); });
  D.textoOriginal = (c) => (porCodigo[c]?.length === 1 ? porCodigo[c][0] : null);

  D.P = cftv.prefixos.map((it) => derivar(it, D));
  D.byPrefixo = Object.fromEntries(D.P.map((p) => [p.p, p]));
  // empresas presentes em cada arquivo (para explicar ausências, ex.: Santa Brígida em 04/09)
  D.empresasPorCol = D.cftv.colunas.map(() => new Set());
  D.P.forEach((p) => { for (let j = 0; j < D.ncol; j++) if (p.g[j] !== ' ') D.empresasPorCol[j].add(p.ed ? p.ed[j] : p.e); });
  D.garagens = [...new Set(D.eventos.flatMap((e) => e.garagens))].sort();
  D.tecnicos = [...new Set(D.forms.map((f) => f.tecnico))].sort((a, b) => a.localeCompare(b, 'pt-BR'));
  return D;
}

function derivar(it, D) {
  const ncol = D.ncol;
  const p = { ...it, recs: 0, nV: 0, nL: 0, nR: 0, camsExist: new Set(), camsProb: new Set(), camsOff: new Set(), camsErr: new Set(), sops: new Set(), empresasIdx: new Set() };
  for (let j = 0; j < ncol; j++) {
    const g = it.g[j];
    if (g === ' ') continue;
    p.recs++;
    if (g === 'V') p.nV++; else if (g === 'L') p.nL++; else if (g === 'R') p.nR++;
    for (let c = 0; c < 6; c++) {
      const code = it.k[j * 6 + c];
      if (camExiste(code)) p.camsExist.add(CAMS[c]);
      if (camProblema(code)) p.camsProb.add(CAMS[c]);
      if (code === 'O') p.camsOff.add(CAMS[c]);
      else if (code >= '1' && code <= '7') p.camsErr.add(CAMS[c]);
    }
    if (it.s[j] !== '_') p.sops.add(it.s.charCodeAt(j) - 65);
    p.empresasIdx.add(it.ed ? it.ed[j] : it.e);
  }
  p.hasOff = p.camsOff.size > 0;
  p.hasErr = p.camsErr.size > 0;
  p.allNormal = p.recs > 0 && p.nV === p.recs;
  p.empresa = it.e >= 0 ? D.cftv.empresas[it.e] : '(não está no CFTV)';
  p.ev = (it.m || []).map((i) => D.eventos[i]);
  p.evByCol = {};
  p.ev.forEach((e) => { if (e.col != null) (p.evByCol[e.col] ||= []).push(e); });
  p.nForms = p.ev.reduce((a, e) => a + e.qtd_formularios, 0);
  p.garagens = new Set(p.ev.flatMap((e) => e.garagens));
  p.tecnicos = new Set(p.ev.flatMap((e) => e.tecnicos));
  p.resultados = new Set(p.ev.map((e) => e.resultado));
  p.pend = p.ev.some((e) => e.pendencia);
  p.normalAntes = p.ev.some((e) => e.veiculo_normal_antes);
  p.probDias = p.nR + p.nL;
  return p;
}

export function registroDoDia(D, p, j) {
  if (p.g[j] === ' ') return null;
  const col = D.cftv.colunas[j];
  const cams = CAMS.map((n, c) => ({ n, code: p.k[j * 6 + c] }));
  return {
    data: col.data, status: p.g[j], cams,
    statusOp: p.s[j] !== '_' ? D.cftv.statusOp[p.s.charCodeAt(j) - 65] : null,
    manutCftv: p.u && p.u[j] >= 0 ? D.cftv.manutCftv[p.u[j]] : null,
    empresa: D.cftv.empresas[p.ed ? p.ed[j] : p.e],
    arquivo: col.arquivo, linha: p.r[j],
  };
}

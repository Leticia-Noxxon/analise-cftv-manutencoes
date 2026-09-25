// Utilidades de formatação e rótulos (textos em português simples)
export const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

export const POS = { 21: 'FRONTAL', 22: 'FRENTE', 23: 'CORREDOR 1', 24: 'CORREDOR 2', 25: 'CORREDOR 3', 26: 'CORREDOR 4' };
export const CAMS = [21, 22, 23, 24, 25, 26];
export const camLabel = (n) => `${POS[n] || 'CÂMERA'} (câm ${n})`;

export const STATUS = {
  V: { nome: 'VERDE', desc: 'Todas as câmeras ONLINE sem erro', cls: 'sV' },
  L: { nome: 'LARANJA', desc: 'Nenhuma câmera OFFLINE, mas há câmera ONLINE com erro', cls: 'sL' },
  R: { nome: 'VERMELHO', desc: 'Pelo menos uma câmera OFFLINE', cls: 'sR' },
  I: { nome: 'INDEFINIDO', desc: 'Texto de câmera não reconhecido', cls: 'sI' },
  S: { nome: 'SEM CÂMERAS', desc: 'Registro sem câmeras instaladas', cls: 'sB' },
  ' ': { nome: 'SEM DADOS', desc: 'Sem registro CFTV nesta data', cls: 'sB' },
};

const ERR_BITS = [[1, 'SD'], [2, 'Login'], [4, 'Gravação']];
export function camInfo(code) {
  // código compacto -> descrição (ver scripts/cftv/interpretacao.py)
  if (code === 'N') return { tipo: 'N', texto: 'ONLINE', cls: 'sV', sd: 'ok', login: 'ok', grav: 'ok', erros: [] };
  if (code === 'O') return { tipo: 'O', texto: 'OFFLINE', cls: 'sR', erros: [] };
  if (code >= '1' && code <= '7') {
    const m = Number(code);
    const erros = ERR_BITS.filter(([b]) => m & b).map(([, n]) => n);
    return { tipo: 'E', texto: 'ONLINE COM ERRO', cls: 'sL', erros, sd: m & 1 ? 'error' : 'ok', login: m & 2 ? 'error' : 'ok', grav: m & 4 ? 'error' : 'ok' };
  }
  if (code === '?') return { tipo: '?', texto: 'NÃO RECONHECIDO', cls: 'sI', erros: [] };
  if (code === '-') return { tipo: '-', texto: 'SEM CÂMERA', cls: 'sB', erros: [] };
  return { tipo: '.', texto: 'FORA DA GRADE', cls: 'sB', erros: [] };
}
export const camExiste = (c) => c === 'N' || c === 'O' || c === '?' || (c >= '1' && c <= '7');
export const camProblema = (c) => c === 'O' || (c >= '1' && c <= '7');

export const RESULTADOS = ['RESOLVIDO', 'RESOLVIDO COM RECORRÊNCIA', 'NÃO RESOLVIDO', 'PARCIALMENTE RESOLVIDO', 'SEM DADOS PARA VALIDAR'];
export const RES_CLS = {
  'RESOLVIDO': 'rOk', 'RESOLVIDO COM RECORRÊNCIA': 'rRec', 'NÃO RESOLVIDO': 'rNo', 'PARCIALMENTE RESOLVIDO': 'rPar', 'SEM DADOS PARA VALIDAR': 'rNd',
};
export const resBadge = (r) => `<span class="badge ${RES_CLS[r] || ''}">${esc(r)}</span>`;
export const statusChip = (s, txt) => `<span class="chip ${STATUS[s]?.cls || 'sB'}">${esc(txt ?? STATUS[s]?.nome ?? s)}</span>`;

export const dm = (iso) => (iso ? `${iso.slice(8, 10)}/${iso.slice(5, 7)}` : '—');
export const dmy = (iso) => (iso ? `${iso.slice(8, 10)}/${iso.slice(5, 7)}/${iso.slice(0, 4)}` : '—');
export const fmtN = (n) => (n == null ? '—' : Number(n).toLocaleString('pt-BR'));
export const pct = (a, b) => (b > 0 ? `${((100 * a) / b).toLocaleString('pt-BR', { maximumFractionDigits: 1 })}%` : '—');
export const plural = (n, s, p) => `${fmtN(n)} ${n === 1 ? s : p}`;

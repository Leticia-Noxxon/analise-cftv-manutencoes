// Abas de análise: Manutenções, Efetividade, Recorrências, Auditoria, Como ler.
import { esc, camLabel, camInfo, CAMS, dm, dmy, fmtN, pct, resBadge, RESULTADOS, RES_CLS, STATUS, statusChip } from './util.js';

export const VALIDAVEIS = ['RESOLVIDO', 'RESOLVIDO COM RECORRÊNCIA', 'NÃO RESOLVIDO', 'PARCIALMENTE RESOLVIDO'];

export function contarResultados(E) {
  const c = Object.fromEntries(RESULTADOS.map((r) => [r, 0]));
  E.forEach((e) => { c[e.resultado]++; });
  const base = VALIDAVEIS.reduce((a, r) => a + c[r], 0);
  return { c, base, taxa: base ? c.RESOLVIDO / base : null, normalizou: base ? (c.RESOLVIDO + c['RESOLVIDO COM RECORRÊNCIA']) / base : null };
}

const card = (t, v, sub = '', cls = '') => `<div class="kpi ${cls}"><div class="kpi-t">${t}</div><div class="kpi-v">${v}</div>${sub ? `<div class="kpi-s">${sub}</div>` : ''}</div>`;

export function htmlKpisResultado(E) {
  const { c, base } = contarResultados(E);
  const nPend = E.filter((e) => e.pendencia).length;
  const nNA = E.filter((e) => e.veiculo_normal_antes).length;
  return `<div class="kpis">
    ${card('Resolvidas', fmtN(c.RESOLVIDO), 'normalizou e não voltou', 'k-ok')}
    ${card('Resolvidas com recorrência', fmtN(c['RESOLVIDO COM RECORRÊNCIA']), 'normalizou, mas a mesma câmera voltou a falhar', 'k-rec')}
    ${card('Não resolvidas', fmtN(c['NÃO RESOLVIDO']), 'o problema continuou', 'k-no')}
    ${card('Parcialmente resolvidas', fmtN(c['PARCIALMENTE RESOLVIDO']), 'parte das câmeras normalizou', 'k-par')}
    ${card('Sem dados para validar', fmtN(c['SEM DADOS PARA VALIDAR']), `${fmtN(nNA)} já estavam normais antes`, 'k-nd')}
    ${card('Com pendência registrada', fmtN(nPend), 'aviso separado do resultado', 'k-pend')}
    ${htmlTaxa(E)}
  </div>`;
}

export function htmlTaxa(E) {
  const { c, base, taxa } = contarResultados(E);
  return card('Taxa de resolução', taxa == null ? '—' : pct(c.RESOLVIDO, base),
    `${fmtN(c.RESOLVIDO)} resolvidas ÷ ${fmtN(base)} validáveis<br><span class="muted">(resolvidas + com recorrência + não resolvidas + parciais)</span>`, 'k-taxa');
}

// ---------------------------------------------------------------- MANUTENÇÕES
export function htmlManutencoes(D, E) {
  const lin = [...E].sort((a, b) => (b.data || '').localeCompare(a.data || '') || a.prefixo - b.prefixo);
  return `<div class="panel">
    <div class="panel-h"><h3>Manutenções (${fmtN(lin.length)} ${lin.length === 1 ? 'evento' : 'eventos'}, ${fmtN(lin.reduce((a, e) => a + e.qtd_formularios, 0))} formulários)</h3>
    <span class="muted small">Um evento = prefixo + data. Clique em uma linha para ver tudo o que o técnico registrou e o antes/depois no CFTV.</span></div>
    <div class="tbl-wrap"><table class="tbl tbl-click" id="tbl-manut"><thead><tr><th>Data</th><th>Hora</th><th>Prefixo</th><th>Empresa (CFTV)</th><th>Técnico</th><th>Câmeras com anomalia (formulário)</th><th>CFTV antes</th><th>Resultado</th><th>Avisos</th></tr></thead><tbody>
    ${lin.map((e) => { const p = D.byPrefixo[e.prefixo]; return `<tr data-ev="${e.idx}"><td>${dm(e.data)}</td><td>${esc(e.horas.join(', '))}</td><td><b>${e.prefixo}</b></td><td>${esc(p ? p.empresa : '')}</td><td>${esc(e.tecnicos.join(', '))}</td>
      <td>${esc(e.cameras_formulario.map((n) => camLabel(n)).join(', ')) || '<span class="muted">nenhuma</span>'}</td>
      <td>${e.antes ? statusChip(e.antes.status, `${dm(e.antes.data)} ${e.antes.status_nome}`) : '<span class="muted">sem registro</span>'}</td>
      <td>${resBadge(e.resultado)}</td><td>${e.pendencia ? '<span class="flag fPend">Pendência</span> ' : ''}${e.veiculo_normal_antes ? '<span class="flag fInfo">Já normal antes</span> ' : ''}${e.qtd_formularios > 1 ? `<span class="flag">${e.qtd_formularios} formulários</span>` : ''}</td></tr>`; }).join('')}
    </tbody></table></div></div>`;
}

// ---------------------------------------------------------------- EFETIVIDADE
function tabelaGrupo(titulo, grupos, nota = '') {
  const linhas = Object.entries(grupos).sort((a, b) => a[0].localeCompare(b[0], 'pt-BR'));
  if (!linhas.length) return '';
  return `<div class="panel"><div class="panel-h"><h3>${esc(titulo)}</h3>${nota ? `<span class="muted small">${nota}</span>` : ''}</div><div class="tbl-wrap"><table class="tbl"><thead><tr><th>${esc(titulo.replace('Por ', ''))}</th><th class="n">Eventos</th>
    ${RESULTADOS.map((r) => `<th class="n"><span class="badge ${RES_CLS[r]}">${r.replace('PARA VALIDAR', '').replace('RESOLVIDO COM RECORRÊNCIA', 'C/ RECORRÊNCIA').replace('PARCIALMENTE RESOLVIDO', 'PARCIAL')}</span></th>`).join('')}<th class="n">Pendência</th><th class="n">Taxa de resolução</th></tr></thead><tbody>
    ${linhas.map(([k, es]) => { const { c, base } = contarResultados(es); return `<tr><td>${esc(k)}</td><td class="n">${es.length}</td>${RESULTADOS.map((r) => `<td class="n">${c[r] || '<span class="muted">0</span>'}</td>`).join('')}<td class="n">${es.filter((e) => e.pendencia).length}</td><td class="n"><b>${pct(c.RESOLVIDO, base)}</b> <span class="muted small">(${c.RESOLVIDO}/${base})</span></td></tr>`; }).join('')}
    </tbody></table></div></div>`;
}

const agrupar = (E, fn) => { const g = {}; E.forEach((e) => { [...new Set(fn(e))].forEach((k) => { (g[k] ||= []).push(e); }); }); return g; };

export function htmlEfetividade(D, E) {
  const porCam = {};
  E.forEach((e) => e.cameras.forEach((c) => { const x = (porCam[c.rotulo] ||= { RESOLVIDO: 0, 'RECORRÊNCIA': 0, 'NÃO RESOLVIDO': 0 }); x[c.resultado] = (x[c.resultado] || 0) + 1; }));
  const { c, base } = contarResultados(E);
  return `
  ${htmlKpisResultado(E)}
  <div class="note"><b>Como a taxa é calculada:</b> Taxa de resolução = RESOLVIDO ÷ (RESOLVIDO + RESOLVIDO COM RECORRÊNCIA + NÃO RESOLVIDO + PARCIALMENTE RESOLVIDO) = ${c.RESOLVIDO} ÷ ${base} = <b>${pct(c.RESOLVIDO, base)}</b>.
    Manutenções “SEM DADOS PARA VALIDAR” ficam fora da conta (inclui veículos que já estavam normais antes). Referência adicional: câmeras que <i>normalizaram</i> (resolvido + com recorrência) = ${pct(c.RESOLVIDO + c['RESOLVIDO COM RECORRÊNCIA'], base)}.
    As tabelas abaixo estão em <b>ordem alfabética</b> e não são um ranking: com poucos casos, a taxa pode variar muito.</div>
  <div class="panel"><div class="panel-h"><h3>Por câmera (resultado de cada câmera que tinha problema antes)</h3><span class="muted small">Uma manutenção pode ter várias câmeras com problema.</span></div>
    <div class="tbl-wrap"><table class="tbl"><thead><tr><th>Câmera</th><th class="n">Câmeras com problema antes</th><th class="n">Normalizou e não voltou</th><th class="n">Normalizou e voltou</th><th class="n">Não normalizou</th><th class="n">% normalizou e não voltou</th></tr></thead><tbody>
    ${CAMS.map((n) => { const x = porCam[camLabel(n)]; if (!x) return ''; const t = x.RESOLVIDO + x['RECORRÊNCIA'] + x['NÃO RESOLVIDO']; return `<tr><td>${esc(camLabel(n))}</td><td class="n">${t}</td><td class="n">${x.RESOLVIDO}</td><td class="n">${x['RECORRÊNCIA']}</td><td class="n">${x['NÃO RESOLVIDO']}</td><td class="n">${pct(x.RESOLVIDO, t)}</td></tr>`; }).join('')}
    </tbody></table></div></div>
  ${tabelaGrupo('Por técnico', agrupar(E, (e) => e.tecnicos))}
  ${tabelaGrupo('Por empresa', agrupar(E, (e) => [D.byPrefixo[e.prefixo]?.empresa || '(não está no CFTV)']), 'Empresa segundo o Relatório CFTV.')}
  ${tabelaGrupo('Por garagem', agrupar(E, (e) => e.garagens), 'Garagem informada no formulário de manutenção.')}
  ${tabelaGrupo('Por tipo de problema', agrupar(E, (e) => e.formsObj.flatMap((f) => f.posicoes.flatMap((x) => x.anomalias))), 'Anomalias marcadas no formulário (um evento aparece em cada tipo marcado).')}
  ${tabelaGrupo('Por tipo de intervenção', agrupar(E, (e) => e.formsObj.flatMap((f) => f.posicoes.flatMap((x) => x.acoes_realizadas))), 'Ações marcadas no formulário (um evento aparece em cada ação marcada).')}`;
}

// ---------------------------------------------------------------- RECORRÊNCIAS
export function htmlRecorrencias(D, L, E) {
  const rec = E.filter((e) => e.recorrencia);
  const novo = E.filter((e) => e.novo_problema_outra_camera || e.surgiu_problema_depois);
  const cols = D.cftv.colunas;
  const off = Object.fromEntries(CAMS.map((n) => [n, 0])); const err = Object.fromEntries(CAMS.map((n) => [n, 0]));
  const tipos = { SD: 0, Login: 0, 'Gravação': 0 };
  L.forEach((p) => { for (let j = 0; j < cols.length; j++) { if (p.g[j] === ' ') continue; for (let c = 0; c < 6; c++) { const k = p.k[j * 6 + c]; if (k === 'O') off[CAMS[c]]++; else if (k >= '1' && k <= '7') { err[CAMS[c]]++; camInfo(k).erros.forEach((t) => { tipos[t]++; }); } } } });
  const topo = [...L].filter((p) => p.probDias > 0).sort((a, b) => b.probDias - a.probDias || b.nR - a.nR || a.p - b.p).slice(0, 25);
  const maxCam = Math.max(1, ...CAMS.map((n) => off[n] + err[n]));
  return `
  <div class="kpis">${card('Manutenções com recorrência', fmtN(rec.length), `a mesma câmera voltou a falhar (${fmtN(rec.filter((e) => e.resultado === 'RESOLVIDO COM RECORRÊNCIA').length)} “com recorrência” + ${fmtN(rec.filter((e) => e.resultado === 'PARCIALMENTE RESOLVIDO').length)} parciais)`, 'k-rec')}
    ${card('Problema novo em outra câmera', fmtN(novo.length), `não é recorrência (${fmtN(novo.filter((e) => e.novo_problema_outra_camera).length)} após correção + ${fmtN(novo.filter((e) => !e.novo_problema_outra_camera).length)} em veículos que estavam normais antes)`, 'k-nd')}
    ${card('Prefixos com recorrência', fmtN(new Set(rec.map((e) => e.prefixo)).size), '', 'k-rec')}</div>
  <div class="grid2">
  <div class="panel"><div class="panel-h"><h3>Câmeras com mais dias de problema</h3><span class="muted small">Soma de câmera-dias nos veículos filtrados.</span></div>
    <div class="bars">${CAMS.map((n) => `<div class="bar-row"><span class="bar-l">${esc(camLabel(n))}</span><span class="bar"><i class="b-off" style="width:${(100 * off[n]) / maxCam}%"></i><i class="b-err" style="width:${(100 * err[n]) / maxCam}%"></i></span><span class="bar-v">${fmtN(off[n])} off · ${fmtN(err[n])} erro</span></div>`).join('')}</div>
    <div class="small"><span class="sq sR"></span> OFFLINE <span class="sq sL"></span> ONLINE com erro</div></div>
  <div class="panel"><div class="panel-h"><h3>Tipos de erro (câmeras ONLINE com erro)</h3><span class="muted small">Uma câmera pode ter mais de um erro no mesmo dia.</span></div>
    <table class="tbl"><tbody>${Object.entries(tipos).map(([t, v]) => `<tr><td>${t}: error</td><td class="n"><b>${fmtN(v)}</b> câmera-dias</td></tr>`).join('')}</tbody></table></div>
  </div>
  <div class="panel"><div class="panel-h"><h3>Recorrências na mesma câmera</h3><span class="muted small">Clique para ver a manutenção.</span></div>
    ${rec.length ? `<div class="tbl-wrap"><table class="tbl tbl-click"><thead><tr><th>Prefixo</th><th>Manutenção</th><th>Técnico</th><th>Resultado</th><th>Normalizou em</th><th>Voltou em</th><th>Câmera(s) que voltaram a falhar</th></tr></thead><tbody>
    ${rec.map((e) => `<tr data-ev="${e.idx}"><td><b>${e.prefixo}</b></td><td>${dm(e.data)}</td><td>${esc(e.tecnicos.join(', '))}</td><td>${resBadge(e.resultado)}</td><td>${dm(e.cameras.filter((c) => c.resultado === 'RECORRÊNCIA').map((c) => c.primeiro_normal).sort()[0])}</td><td>${dm(e.recorrencia.data)}</td><td>${e.recorrencia.problemas.map((x) => `${esc(x.rotulo)} — ${esc(x.descricao)}`).join('<br>')}</td></tr>`).join('')}</tbody></table></div>` : '<p class="muted">Nenhuma recorrência com os filtros atuais.</p>'}</div>
  <div class="panel"><div class="panel-h"><h3>Problema novo em outra câmera (depois da manutenção)</h3><span class="muted small">Informativo: uma câmera diferente da que tinha problema passou a falhar.</span></div>
    ${novo.length ? `<div class="tbl-wrap"><table class="tbl tbl-click"><thead><tr><th>Prefixo</th><th>Manutenção</th><th>Resultado</th><th>Quando</th><th>Câmera(s)</th></tr></thead><tbody>
    ${novo.map((e) => { const x = e.novo_problema_outra_camera || e.surgiu_problema_depois; return `<tr data-ev="${e.idx}"><td><b>${e.prefixo}</b></td><td>${dm(e.data)}</td><td>${resBadge(e.resultado)}</td><td>${dm(x.data)}</td><td>${x.problemas.map((y) => `${esc(y.rotulo)} — ${esc(y.descricao)}`).join('<br>')}</td></tr>`; }).join('')}</tbody></table></div>` : '<p class="muted">Nenhum caso com os filtros atuais.</p>'}</div>
  <div class="panel"><div class="panel-h"><h3>Prefixos com mais dias com problema (top 25 dos filtrados)</h3><span class="muted small">Clique para abrir a linha do tempo.</span></div>
    <div class="tbl-wrap"><table class="tbl tbl-click"><thead><tr><th>Prefixo</th><th>Empresa</th><th class="n">Dias vermelhos</th><th class="n">Dias laranjas</th><th class="n">Dias com registro</th><th class="n">Manutenções</th></tr></thead><tbody>
    ${topo.map((p) => `<tr data-p="${p.p}"><td><b>${p.p}</b></td><td>${esc(p.empresa)}</td><td class="n">${p.nR}</td><td class="n">${p.nL}</td><td class="n">${p.recs}</td><td class="n">${p.nForms || ''}</td></tr>`).join('')}</tbody></table></div></div>`;
}

// ---------------------------------------------------------------- AUDITORIA
export function htmlAuditoria(D) {
  const m = D.meta;
  return `
  <div class="note">Esta aba mostra de onde veio cada dado e como os textos originais foram interpretados. Nenhum arquivo original foi alterado.</div>
  <div class="panel"><div class="panel-h"><h3>Como cada texto de câmera foi interpretado</h3></div>
    <div class="tbl-wrap"><table class="tbl"><thead><tr><th>Texto original na planilha</th><th class="n">Ocorrências</th><th>Interpretação</th><th>Conta na cor do dia?</th></tr></thead><tbody>
    ${m.auditoria_textos.map((t) => `<tr><td><code>${esc(t.original)}</code></td><td class="n">${fmtN(t.quantidade)}</td><td><span class="sq ${camInfo(t.codigo).cls}"></span>${esc(t.classificacao)}${t.erros.length ? ` (${t.erros.join(', ')})` : ''}${t.codigo === '-' ? ' — a câmera não existe (não instalada) neste veículo nesse dia' : ''}${t.codigo === '.' ? ' — célula vazia' : ''}</td>
      <td>${['N', 'O'].includes(t.codigo) || (t.codigo >= '1' && t.codigo <= '7') ? 'Sim' : 'Não (câmera ignorada)'}</td></tr>`).join('')}
    </tbody></table></div></div>
  <div class="panel"><div class="panel-h"><h3>Arquivos CFTV utilizados</h3></div>
    <div class="tbl-wrap"><table class="tbl"><thead><tr><th>Arquivo</th><th>Aba utilizada</th><th>Abas ignoradas (motivo)</th><th class="n">Registros</th><th class="n">Linhas vazias</th><th>Data confere</th></tr></thead><tbody>
    ${m.arquivos_cftv.map((a) => `<tr><td>${esc(a.arquivo)}</td><td>${esc(a.aba_utilizada)}</td><td>${a.abas_ignoradas.map((x) => `${esc(x.aba)}: ${esc(x.motivo)}`).join('<br>')}</td><td class="n">${fmtN(a.registros)}</td><td class="n">${fmtN(a.linhas_vazias_desconsideradas)}</td><td>${a.data_confere_com_nome ? 'Sim' : '<b class="t-red">Não</b>'}</td></tr>`).join('')}
    </tbody></table></div>
    <p class="small muted">Datas sem arquivo (células brancas): ${D.cftv.colunas.filter((c) => !c.tem_arquivo && !c.fora_periodo).map((c) => c.rotulo).join(', ')}.${D.cftv.colunas.some((c) => c.fora_periodo) ? ` Fora do período do CFTV (só manutenções): ${D.cftv.colunas.filter((c) => c.fora_periodo).map((c) => c.rotulo).join(', ')}.` : ''}</p></div>
  <div class="panel"><div class="panel-h"><h3>Arquivo de manutenções</h3></div>
    <div class="kvs">${[['Arquivo', m.arquivo_manutencao.arquivo], ['Aba utilizada', m.arquivo_manutencao.aba_utilizada], ['Abas ignoradas', m.arquivo_manutencao.abas_ignoradas.map((x) => `${x.aba}: ${x.motivo}`).join('; ')], ['Formulários', m.arquivo_manutencao.registros], ['Nomes padronizados', Object.entries(m.arquivo_manutencao.tecnicos_padronizados).map(([a, b]) => `“${a}” → “${b}”`).join('; ') || '—']].map(([k, v]) => `<div class="kv"><span>${k}</span><b>${esc(v)}</b></div>`).join('')}</div></div>
  <div class="panel"><div class="panel-h"><h3>Inconsistências e alertas encontrados (${m.inconsistencias.length})</h3></div>
    <div class="tbl-wrap"><table class="tbl"><thead><tr><th>Tipo</th><th>Onde</th><th>Detalhe</th></tr></thead><tbody>
    ${m.inconsistencias.map((i) => `<tr><td>${esc(i.tipo)}</td><td>${esc(i.onde)}</td><td>${esc(i.detalhe)}</td></tr>`).join('')}
    </tbody></table></div></div>
  <div class="panel"><div class="panel-h"><h3>Regras aplicadas (resumo)</h3></div>${htmlRegras()}</div>`;
}

function htmlRegras() {
  return `<ul class="rules">
    <li><b>Cor do dia:</b> vermelho se ao menos uma câmera está OFFLINE; laranja se nenhuma está OFFLINE mas alguma está ONLINE com erro (SD, Login ou Gravação); verde se todas as câmeras existentes estão ONLINE sem erro; branco se não há registro.</li>
    <li><b>“-” na planilha</b> = o veículo não tem essa câmera: ela é ignorada (não conta como OFFLINE nem erro).</li>
    <li><b>Câmeras:</b> 21 = FRONTAL, 22 = FRENTE, 23 = CORREDOR 1, 24 = CORREDOR 2, 25 = CORREDOR 3, 26 = CORREDOR 4. Notação “C1…C6” escrita pelo técnico é exibida como informada, sem conversão.</li>
    <li><b>Antes</b> = último registro CFTV anterior à data da manutenção. <b>Dia da manutenção</b> = mostrado à parte, não conta como antes nem depois. <b>Depois</b> = registros posteriores até a véspera da próxima manutenção do mesmo prefixo (ou até o último dia do período).</li>
    <li><b>Câmeras avaliadas</b> = as que tinham problema no registro anterior. Cada câmera: normalizou e não voltou / normalizou e voltou (recorrência) / não normalizou.</li>
    <li><b>Resultado da manutenção:</b> RESOLVIDO (todas normalizaram e não voltaram); RESOLVIDO COM RECORRÊNCIA (normalizaram, mas alguma voltou a falhar); PARCIALMENTE RESOLVIDO (parte normalizou); NÃO RESOLVIDO (nenhuma normalizou); SEM DADOS PARA VALIDAR (sem registro antes/depois, fora do período, ou sem problema no CFTV antes).</li>
    <li><b>Veículo já estava normal antes:</b> aviso separado; o resultado formal fica “SEM DADOS PARA VALIDAR”, pois não havia problema no CFTV para confirmar a solução.</li>
    <li><b>Pendência:</b> aviso separado, identificado por palavras-chave no formulário (o trecho encontrado é exibido). Não altera o resultado, que é baseado no CFTV.</li>
    <li><b>Problema novo em outra câmera</b> é informado à parte e não é contado como recorrência.</li>
  </ul>`;
}

export function htmlComoLer(D) {
  return `<div class="panel howto">
    <h3>Como ler este painel</h3>
    <ol>
      <li><b>Matriz</b>: cada linha é um veículo (prefixo) e cada coluna é um dia. A cor mostra a situação das câmeras naquele dia:
        <div class="legend-inline">${statusChip('V', 'Verde: todas ONLINE sem erro')} ${statusChip('L', 'Laranja: alguma câmera com erro')} ${statusChip('R', 'Vermelho: alguma câmera OFFLINE')} ${statusChip(' ', 'Branco: sem dados')} <span><span class="dot-mini"></span> Bolinha azul: houve manutenção</span></div></li>
      <li>Passe o mouse sobre um quadrado para ver as câmeras daquele dia. <b>Clique</b> no quadrado para abrir os detalhes, na <b>bolinha azul</b> para ver a manutenção e no <b>número do prefixo</b> para ver a linha do tempo completa.</li>
      <li>A matriz abre mostrando só os <b>veículos com manutenção</b>. Use “Todos os veículos” para ver os ${fmtN(D.P.filter((p) => p.recs).length)} prefixos.</li>
      <li><b>Manutenções</b>: lista de todas as visitas do técnico, com o resultado.</li>
      <li><b>Efetividade</b>: quantas manutenções resolveram o problema, por técnico, empresa, garagem, câmera e tipo de problema.</li>
      <li><b>Recorrências</b>: casos em que o problema voltou e câmeras que mais falham.</li>
      <li><b>Auditoria</b>: de onde veio cada dado e como os textos das planilhas foram interpretados.</li>
      <li>O botão <b>Exportar Excel</b> baixa os dados já filtrados.</li>
    </ol>
    <h3>Regras</h3>${htmlRegras()}
  </div>`;
}

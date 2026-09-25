// Exportação dos resultados filtrados para Excel (SheetJS) ou CSV.
import * as XLSX from 'xlsx';
import { camLabel, camInfo, camExiste, CAMS, dmy, STATUS } from './util.js';
import { registroDoDia } from './data.js';
import { contarResultados } from './tabs.js';

function planilhas(D, L, E, filtrosTxt) {
  const { c, base, taxa } = contarResultados(E);
  const resumo = [
    { Item: 'Gerado em', Valor: D.meta.gerado_em },
    { Item: 'Filtros', Valor: filtrosTxt },
    { Item: 'Veículos exibidos', Valor: L.length },
    { Item: 'Veículos com registro CFTV', Valor: L.filter((p) => p.recs).length },
    { Item: 'Câmeras analisadas', Valor: L.reduce((a, p) => a + p.camsExist.size, 0) },
    { Item: 'Veículos com câmera OFFLINE', Valor: L.filter((p) => p.hasOff).length },
    { Item: 'Veículos com câmera com erro', Valor: L.filter((p) => p.hasErr).length },
    { Item: 'Manutenções (formulários)', Valor: E.reduce((a, e) => a + e.qtd_formularios, 0) },
    { Item: 'Manutenções (eventos prefixo+data)', Valor: E.length },
    ...Object.entries(c).map(([k, v]) => ({ Item: k, Valor: v })),
    { Item: 'Com pendência', Valor: E.filter((e) => e.pendencia).length },
    { Item: 'Veículo já estava normal antes', Valor: E.filter((e) => e.veiculo_normal_antes).length },
    { Item: 'Taxa de resolução', Valor: taxa == null ? '' : `${(100 * taxa).toFixed(1)}% (${c.RESOLVIDO}/${base})` },
    { Item: 'Fórmula', Valor: 'RESOLVIDO ÷ (RESOLVIDO + RESOLVIDO COM RECORRÊNCIA + NÃO RESOLVIDO + PARCIALMENTE RESOLVIDO)' },
  ];
  const hist = [];
  L.forEach((p) => {
    D.cftv.colunas.forEach((col, j) => {
      const r = registroDoDia(D, p, j);
      const evs = p.evByCol[j];
      if (!r && !evs) return;
      const row = { Prefixo: p.p, Data: dmy(col.data), Empresa: r ? r.empresa : p.empresa, 'Status geral': STATUS[p.g[j]].nome };
      CAMS.forEach((n, c2) => { const code = p.k[j * 6 + c2]; const i = camInfo(code); row[camLabel(n)] = r ? (camExiste(code) ? `${i.texto}${i.erros.length ? ` (${i.erros.join(', ')})` : ''}` : i.texto) : ''; });
      row['Status operacional'] = r?.statusOp || '';
      row['Manutenção no dia'] = evs ? evs.map((e) => `${e.tecnicos.join(', ')} ${e.horas.join(', ')} — ${e.resultado}`).join(' | ') : '';
      row['Arquivo'] = r?.arquivo || ''; row['Linha Excel'] = r?.linha || '';
      hist.push(row);
    });
  });
  const manut = [];
  E.forEach((e) => e.formsObj.forEach((f) => {
    manut.push({
      Prefixo: f.prefixo, Data: dmy(f.data), Hora: f.hora, 'Técnico': f.tecnico, Garagem: f.garagem, Tecnologia: f.tecnologia, ID: f.id_formulario,
      'Anomalias': f.posicoes.filter((x) => x.anomalias.length).map((x) => `${x.rotulo}: ${x.anomalias.join(', ')}`).join(' | '),
      'Ações': f.posicoes.filter((x) => x.acoes_realizadas.length).map((x) => `${x.rotulo}: ${x.acoes_realizadas.join(', ')}`).join(' | '),
      'Câmeras citadas no texto': f.cameras_citadas_texto.map(camLabel).join(', '), 'Notação C (informada)': f.notacao_c_texto.join(', '),
      'Série instalada': f.equipamento.instalado.series.join(', '), 'MAC instalado': f.equipamento.instalado.macs.join(', '),
      'Série retirada': f.equipamento.retirado.series.join(', '), 'MAC retirado': f.equipamento.retirado.macs.join(', '),
      'Pendência': f.pendencia_trechos.map((t) => t.trecho).join(' | '), 'Observações': f.observacoes || '', Alertas: f.alertas.join(' | '), 'Linha Excel': f.linha_excel,
    });
  }));
  const res = E.map((e) => ({
    Prefixo: e.prefixo, 'Data manutenção': dmy(e.data), 'Técnico(s)': e.tecnicos.join(', '), Formulários: e.qtd_formularios,
    'Antes (data)': dmy(e.antes?.data), 'Antes (status)': e.antes?.status_nome || '', 'Câmeras com problema antes': (e.antes?.problemas || []).map((x) => `${x.rotulo} ${x.descricao}`).join(' | '),
    'Dia da manutenção (status)': e.dia?.status_nome || '', 'Normalizou em': dmy(e.normalizacao?.primeiro_normal), 'Registros até normalizar': e.normalizacao?.registros_ate_normalizar ?? '',
    'Recorrência (data)': dmy(e.recorrencia?.data), 'Problema novo outra câmera': dmy((e.novo_problema_outra_camera || e.surgiu_problema_depois)?.data),
    Resultado: e.resultado, Motivo: e.motivo, 'Pendência': e.pendencia ? 'SIM' : '', 'Já normal antes': e.veiculo_normal_antes ? 'SIM' : '', 'História': e.historia.join(' '),
  }));
  const rec = E.filter((e) => e.recorrencia).map((e) => ({ Prefixo: e.prefixo, 'Manutenção': dmy(e.data), Resultado: e.resultado, 'Normalizou em': dmy(e.cameras.filter((c) => c.resultado === 'RECORRÊNCIA').map((c) => c.primeiro_normal).sort()[0]), 'Voltou em': dmy(e.recorrencia.data), 'Câmeras': e.recorrencia.problemas.map((x) => `${x.rotulo} ${x.descricao}`).join(' | ') }));
  return { Resumo: resumo, 'Histórico por prefixo': hist, 'Manutenções': manut, 'Resultado das manutenções': res, 'Recorrências': rec };
}

export function exportar(D, L, E, filtrosTxt, formato = 'xlsx') {
  const sh = planilhas(D, L, E, filtrosTxt);
  const stamp = new Date().toISOString().slice(0, 10);
  if (formato === 'xlsx') {
    const wb = XLSX.utils.book_new();
    Object.entries(sh).forEach(([nome, rows]) => XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(rows.length ? rows : [{ Aviso: 'Sem dados para os filtros' }]), nome.slice(0, 31)));
    XLSX.writeFile(wb, `analise_cftv_${stamp}.xlsx`);
  } else {
    const ws = XLSX.utils.json_to_sheet(sh[formato] || []);
    const csv = '\ufeff' + XLSX.utils.sheet_to_csv(ws, { FS: ';' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    a.download = `${formato.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, '_').toLowerCase()}_${stamp}.csv`;
    a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  }
}
export const NOMES_PLANILHAS = ['Resumo', 'Histórico por prefixo', 'Manutenções', 'Resultado das manutenções', 'Recorrências'];

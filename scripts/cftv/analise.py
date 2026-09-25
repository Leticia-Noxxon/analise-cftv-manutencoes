"""F8/F9 — Relação manutenção × CFTV, antes/depois, recorrência e classificação (§18–§24).

Regras principais (REGRAS_PROJETO.md §7, §8, §17):
- Evento (intervenção) = mesmo prefixo + mesma data literal do formulário (Q4/Q5).
- ANTES = último registro CFTV com data < data do evento. DIA = registro na própria data (exibido à parte,
  não conta como antes nem depois). DEPOIS = registros com data > data do evento e < data do próximo evento
  do mesmo prefixo (janela), limitados à base disponível.
- "Problema original" = câmeras com OFFLINE ou ONLINE COM ERRO no registro ANTES.
- Câmera: RESOLVIDO (normalizou e não voltou) | RECORRÊNCIA (normalizou e voltou a falhar) |
  NÃO RESOLVIDO (nunca normalizou) | SEM DADOS (câmera sem informação nos registros posteriores).
- Evento: todas RESOLVIDO -> RESOLVIDO; todas normalizaram e alguma voltou -> RESOLVIDO COM RECORRÊNCIA;
  nenhuma normalizou -> NÃO RESOLVIDO; parte normalizou -> PARCIALMENTE RESOLVIDO;
  sem registro anterior, sem registro posterior, sem problema antes (Q17) -> SEM DADOS PARA VALIDAR.
- Problema em câmera que não fazia parte do problema original NÃO é recorrência (§22): nota
  "Problema original normalizado. Novo problema identificado em outra câmera."
- PENDÊNCIA é marcador separado (Q18). "Veículo já estava normal antes da manutenção" é marcador (Q17).
"""
import datetime as dt

from . import config
from .config import rotulo_camera
from .interpretacao import codigo_e_problema, codigo_existe, descrever_codigo, NOME_STATUS

SEVERIDADE = {'R': 0, 'L': 1, 'I': 2, 'V': 3, 'S': 4}


def dm(d):
    return d.strftime('%d/%m') if d else '—'


def _d(s):
    return dt.date.fromisoformat(s) if isinstance(s, str) else s


def indexar_cftv(df):
    """{prefixo: {data: registro}}; duplicidade prefixo+data (Q5): mantém a pior situação e registra."""
    idx, duplicados = {}, []
    cols = ['prefixo', 'data', 'codigos', 'status_geral', 'empresa', 'status_operacional_cftv',
            'ultima_manutencao_cftv', 'arquivo_origem', 'linha_excel']
    for r in df[cols].itertuples(index=False):
        rec = r._asdict()
        d = idx.setdefault(rec['prefixo'], {})
        if rec['data'] in d:
            duplicados.append((rec['prefixo'], rec['data']))
            if SEVERIDADE[rec['status_geral']] >= SEVERIDADE[d[rec['data']]['status_geral']]:
                continue
        d[rec['data']] = rec
    return idx, duplicados


def problemas_do_registro(rec, cameras=None):
    out = []
    for i, n in enumerate(config.CAMERAS):
        c = rec['codigos'][i]
        if codigo_e_problema(c) and (cameras is None or n in cameras):
            out.append({'camera': n, 'rotulo': rotulo_camera(n), 'codigo': c, 'descricao': descrever_codigo(c)})
    return out


def _txt_problemas(ps):
    return '; '.join(f"{p['rotulo']} {p['descricao']}" for p in ps) or 'nenhum'


def _cod(rec, n):
    return rec['codigos'][config.CAMERAS.index(n)]


def resumo_registro(rec):
    if rec is None:
        return None
    return {'data': rec['data'].isoformat(), 'status': rec['status_geral'],
            'status_nome': NOME_STATUS[rec['status_geral']], 'problemas': problemas_do_registro(rec),
            'arquivo': rec['arquivo_origem'], 'linha_excel': rec['linha_excel']}


def classificar_camera(n, depois):
    seq = [(r['data'], _cod(r, n)) for r in depois if codigo_existe(_cod(r, n)) and _cod(r, n) != '?']
    if not seq:
        return {'camera': n, 'resultado': 'SEM DADOS', 'primeiro_normal': None, 'recorrencia': None, 'sequencia': []}
    i_norm = next((i for i, (_, c) in enumerate(seq) if c == 'N'), None)
    res = {'camera': n, 'rotulo': rotulo_camera(n), 'sequencia': [(d.isoformat(), c) for d, c in seq],
           'primeiro_normal': None, 'recorrencia': None}
    if i_norm is None:
        res['resultado'] = config.NAO_RESOLVIDO
        return res
    res['primeiro_normal'] = seq[i_norm][0].isoformat()
    rec = next(((d, c) for d, c in seq[i_norm + 1:] if codigo_e_problema(c)), None)
    if rec:
        res['resultado'] = 'RECORRÊNCIA'
        res['recorrencia'] = {'data': rec[0].isoformat(), 'codigo': rec[1], 'descricao': descrever_codigo(rec[1])}
    else:
        res['resultado'] = config.RESOLVIDO
    return res


def analisar_evento(prefixo, data, forms, recs, janela_fim):
    """recs: {data: registro} do prefixo; janela_fim: data do próximo evento (exclusiva) ou None."""
    datas = sorted(recs)
    antes = next((recs[d] for d in reversed(datas) if d < data), None)
    dia = recs.get(data)
    depois = [recs[d] for d in datas if d > data and (janela_fim is None or d < janela_fim)]
    posteriores_fora_janela = [d for d in datas if janela_fim is not None and d >= janela_fim]
    tecnicos = sorted({f['tecnico'] for f in forms})
    cams_form = sorted({c for f in forms for c in f['cameras_com_anomalia']} | {c for f in forms for c in f['cameras_citadas_texto']})
    ev = {
        'id': f'{prefixo}_{data.isoformat()}', 'prefixo': prefixo, 'data': data.isoformat(),
        'forms': [f['id_form'] for f in forms], 'qtd_formularios': len(forms),
        'horas': [f['hora'] for f in forms], 'tecnicos': tecnicos,
        'garagens': sorted({f['garagem'] for f in forms if f['garagem']}),
        'cameras_formulario': cams_form,
        'fora_periodo': data > config.PERIODO_FIM or data < config.PERIODO_INICIO,
        'antes': resumo_registro(antes), 'dia': resumo_registro(dia),
        'depois': [resumo_registro(r) for r in depois],
        'janela_fim': janela_fim.isoformat() if janela_fim else None,
        'pendencia': any(f['pendencia'] for f in forms),
        'pendencia_trechos': [t for f in forms for t in f['pendencia_trechos']],
        'veiculo_normal_antes': False, 'cameras': [], 'duracao_antes': None, 'normalizacao': None,
        'permanencia': None, 'recorrencia': None, 'novo_problema_outra_camera': None,
        'surgiu_problema_depois': None, 'prefixo_no_cftv': bool(recs),
    }
    hist = []
    alvo = [p['camera'] for p in problemas_do_registro(antes)] if antes else []

    # ---- ANTES ----
    if antes is None:
        hist.append('Antes: não há registro CFTV anterior à manutenção.' if recs else
                    'Este prefixo não aparece em nenhum Relatório CFTV.')
    else:
        ps = problemas_do_registro(antes)
        hist.append(f"Antes: último registro em {dm(antes['data'])} — {NOME_STATUS[antes['status_geral']]}"
                    + (f". Problema: {_txt_problemas(ps)}." if ps else '. Todas as câmeras ONLINE sem erro.'))
        if alvo:
            # duração do problema (registros consecutivos com problema nas câmeras-alvo, voltando no tempo)
            streak = []
            for d in reversed([d for d in datas if d < data]):
                if any(codigo_e_problema(_cod(recs[d], n)) for n in alvo):
                    streak.append(d)
                elif any(_cod(recs[d], n) == 'N' for n in alvo):
                    break
            ini, fim = min(streak), max(streak)
            desde_inicio = ini == datas[0]
            ev['duracao_antes'] = {'primeiro_dia': ini.isoformat(), 'ultimo_registro_com_problema': fim.isoformat(),
                                   'registros_com_problema': len(streak), 'dias_corridos': (fim - ini).days + 1,
                                   'desde_primeiro_registro_disponivel': desde_inicio}
            hist.append(f"O problema aparece desde {dm(ini)}{' (já existia no primeiro registro disponível)' if desde_inicio else ''}: "
                        f"{len(streak)} registro(s) com problema, {(fim - ini).days + 1} dia(s) corrido(s) até {dm(fim)}.")

    # ---- MANUTENÇÃO ----
    for f in forms:
        anom = '; '.join(f"{d['rotulo']}: {', '.join(d['anomalias'])}" for d in f['posicoes'] if d['anomalias']) or 'nenhuma anomalia marcada'
        hist.append(f"Manutenção em {dm(data)} às {f['hora']} — técnico {f['tecnico']}. Anomalias: {anom}.")
    if dia:
        hist.append(f"No dia da manutenção ({dm(data)}) o CFTV mostrava {NOME_STATUS[dia['status_geral']]} "
                    f"(registro exibido à parte: não conta como antes nem depois).")
    else:
        hist.append(f"Não há registro CFTV no dia da manutenção ({dm(data)}).")

    # ---- DEPOIS / classificação ----
    resultado, motivo = None, None
    if not recs:
        resultado, motivo = config.SEM_DADOS, 'prefixo inexistente no CFTV'
    elif antes is None:
        resultado, motivo = config.SEM_DADOS, 'sem registro CFTV anterior à manutenção'
    elif antes['status_geral'] in ('I', 'S'):
        resultado, motivo = config.SEM_DADOS, 'situação anterior indefinida'
    elif not depois:
        resultado = config.SEM_DADOS
        if ev['fora_periodo']:
            motivo = 'manutenção fora do período do CFTV (sem registros posteriores)'
        elif posteriores_fora_janela:
            motivo = 'nova manutenção no mesmo prefixo antes do próximo registro CFTV'
        else:
            motivo = 'sem registro CFTV posterior à manutenção'
    if depois:
        hist.append('Depois: ' + ', '.join(f"{dm(_d(r['data']))} {NOME_STATUS[r['status']]}" for r in ev['depois']) + '.')

    if resultado is None and not alvo:
        # Q17: já estava normal antes — marcador; resultado formal SEM DADOS PARA VALIDAR
        ev['veiculo_normal_antes'] = True
        resultado, motivo = config.SEM_DADOS, 'sem problema no CFTV antes da manutenção (não há o que validar)'
        hist.append('Veículo já estava normal antes da manutenção.')
        prob = next((r for r in depois if problemas_do_registro(r)), None)
        if prob:
            ps = problemas_do_registro(prob)
            ev['surgiu_problema_depois'] = {'data': prob['data'].isoformat(), 'problemas': ps}
            hist.append(f"Surgiu problema depois, em {dm(prob['data'])}: {_txt_problemas(ps)}.")
        else:
            hist.append('Continuou normal em todos os registros posteriores disponíveis.')

    if resultado is None:
        cams = [classificar_camera(n, depois) for n in alvo]
        ev['cameras'] = cams
        com_dados = [c for c in cams if c['resultado'] != 'SEM DADOS']
        rs = {c['resultado'] for c in com_dados}
        if not com_dados:
            resultado, motivo = config.SEM_DADOS, 'câmeras do problema original sem informação nos registros posteriores'
        elif rs == {config.RESOLVIDO}:
            resultado, motivo = config.RESOLVIDO, 'o problema original desapareceu e não voltou nos registros posteriores'
        elif rs <= {config.RESOLVIDO, 'RECORRÊNCIA'}:
            resultado, motivo = config.RESOLVIDO_REC, 'normalizou, mas a mesma câmera voltou a apresentar problema'
        elif rs == {config.NAO_RESOLVIDO}:
            resultado, motivo = config.NAO_RESOLVIDO, 'o problema original permaneceu em todos os registros posteriores'
        else:
            resultado, motivo = config.PARCIAL, 'parte das câmeras com problema normalizou e parte não'
        # normalização do conjunto (todas as câmeras-alvo normais ao mesmo tempo)
        i_norm = next((i for i, r in enumerate(depois)
                       if all(_cod(r, n) == 'N' or not codigo_existe(_cod(r, n)) for n in alvo)
                       and any(_cod(r, n) == 'N' for n in alvo)), None)
        if i_norm is not None:
            pn = depois[i_norm]
            ev['normalizacao'] = {'normalizou': True, 'primeiro_normal': pn['data'].isoformat(),
                                  'registros_ate_normalizar': i_norm + 1, 'dias_ate_normalizar': (pn['data'] - data).days}
            fim_normal, n_norm, rec = pn['data'], 0, None
            for r in depois[i_norm:]:
                ps = [p for p in problemas_do_registro(r) if p['camera'] in alvo]
                if ps:
                    rec = (r['data'], ps)
                    break
                n_norm += 1
                fim_normal = r['data']
            ev['permanencia'] = {'registros_normais': n_norm, 'dias_corridos': (fim_normal - pn['data']).days + 1,
                                 'ate': fim_normal.isoformat()}
            hist.append(f"Normalizou no {i_norm + 1}º registro após a manutenção ({dm(pn['data'])}), "
                        f"{(pn['data'] - data).days} dia(s) corrido(s) depois.")
            if rec:
                ev['recorrencia'] = {'data': rec[0].isoformat(), 'mesma_camera': True, 'problemas': rec[1]}
                hist.append(f"Permaneceu normal por {n_norm} registro(s) ({(fim_normal - pn['data']).days + 1} dia(s) corrido(s)), até {dm(fim_normal)}.")
                hist.append(f"O problema voltou em {dm(rec[0])} na mesma câmera: {_txt_problemas(rec[1])}.")
            else:
                hist.append(f"Permaneceu normal por {n_norm} registro(s) ({(fim_normal - pn['data']).days + 1} dia(s) corrido(s)) até o último registro disponível ({dm(fim_normal)}).")
        else:
            ev['normalizacao'] = {'normalizou': False}
            norm = [c for c in com_dados if c['primeiro_normal']]
            if norm:
                hist.append('Normalizou só em parte: ' + '; '.join(f"{c['rotulo']} normalizou em {dm(_d(c['primeiro_normal']))}" for c in norm) + '.')
            nao = [c for c in com_dados if c['resultado'] == config.NAO_RESOLVIDO]
            if nao:
                hist.append('Continuou com problema: ' + ', '.join(c['rotulo'] for c in nao) + '.')
        # recorrência por câmera (se alguma câmera voltou antes do conjunto normalizar)
        reco = [c for c in cams if c['resultado'] == 'RECORRÊNCIA']
        if reco and not ev['recorrencia']:
            primeira = min(reco, key=lambda c: c['recorrencia']['data'])
            ev['recorrencia'] = {'data': primeira['recorrencia']['data'], 'mesma_camera': True,
                                 'problemas': [{'camera': c['camera'], 'rotulo': rotulo_camera(c['camera']),
                                                'codigo': c['recorrencia']['codigo'], 'descricao': c['recorrencia']['descricao']}
                                               for c in reco if c['recorrencia']['data'] == primeira['recorrencia']['data']]}
            hist.append(f"A mesma câmera voltou a falhar em {dm(_d(ev['recorrencia']['data']))}: {_txt_problemas(ev['recorrencia']['problemas'])}.")
        # novo problema em outra câmera (§22)
        for r in depois:
            outras = [p for p in problemas_do_registro(r) if p['camera'] not in alvo]
            if outras:
                ev['novo_problema_outra_camera'] = {'data': r['data'].isoformat(), 'problemas': outras}
                orig_ok = any(c['primeiro_normal'] for c in cams)
                hist.append(('Problema original normalizado. ' if orig_ok else '')
                            + f"Novo problema identificado em outra câmera em {dm(r['data'])}: {_txt_problemas(outras)} (não é recorrência).")
                break

    if ev['pendencia']:
        hist.append('Pendência registrada pelo técnico: ' + ' | '.join(t['trecho'] for t in ev['pendencia_trechos']))
    hist.append(f'Resultado: {resultado}' + (f' — {motivo}.' if motivo else '.'))
    ev['resultado'] = resultado
    ev['motivo'] = motivo
    ev['historia'] = hist
    ev['cameras_problema_antes'] = alvo
    return ev


def montar_eventos(forms, idx_cftv):
    grupos = {}
    sem_data = []
    for f in forms:
        if not f['data']:
            sem_data.append(f['id_form'])
            continue
        grupos.setdefault((f['prefixo'], _d(f['data'])), []).append(f)
    por_prefixo = {}
    for (p, d) in grupos:
        por_prefixo.setdefault(p, []).append(d)
    eventos = []
    for p, ds in por_prefixo.items():
        ds = sorted(ds)
        for i, d in enumerate(ds):
            fs = sorted(grupos[(p, d)], key=lambda f: f['datahora'])
            eventos.append(analisar_evento(p, d, fs, idx_cftv.get(p, {}), ds[i + 1] if i + 1 < len(ds) else None))
    eventos.sort(key=lambda e: (e['data'], e['prefixo']))
    return eventos, sem_data

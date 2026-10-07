"""Testes obrigatórios da especificação (§45) + regras decididas pela usuária (Q2, Q4, Q17)."""
import datetime as dt

import openpyxl

from conftest import ERR, OFF, OK, form, registro
from cftv import analise, config, exportar, manutencao
from cftv.interpretacao import interpretar_camera, normalizar_posicao, status_geral


def cods(*textos):
    return ''.join(interpretar_camera(t)['codigo'] for t in textos)


# 1 ---------------------------------------------------------------
def test_1_todas_online_ok_verde():
    assert status_geral(cods(OK, OK, OK)) == 'V'


# 2 ---------------------------------------------------------------
def test_2_uma_online_com_erro_nenhuma_offline_laranja():
    assert status_geral(cods(OK, ERR, OK)) == 'L'
    it = interpretar_camera(ERR)
    assert it['classificacao'] == 'ONLINE COM ERRO' and it['erros'] == ['SD', 'Gravação']
    assert interpretar_camera('ONLINE (SD: ok, Login: error, Gravação: ok)')['erros'] == ['Login']


# 3 ---------------------------------------------------------------
def test_3_uma_offline_vermelho_mesmo_com_outras_online():
    assert status_geral(cods(OK, OK, OFF)) == 'R'
    assert status_geral(cods(ERR, OFF, OK)) == 'R'


# 4 ---------------------------------------------------------------
def test_4_sem_registro_fica_branco(d, df_de):
    df = df_de([registro(100, d(1), {21: OK}), registro(100, d(3), {21: OFF})])
    m = exportar.montar_matriz(df, [])
    item = m['prefixos'][0]
    col = {c['data']: i for i, c in enumerate(m['colunas'])}
    assert len(m['colunas']) == 24  # 01/09 a 24/09: todas as datas aparecem
    assert item['g'][col['2026-09-01']] == 'V'
    assert item['g'][col['2026-09-02']] == ' '  # BRANCO (sem dados), nunca OFFLINE
    assert item['g'][col['2026-09-03']] == 'R'
    assert set(item['g']) <= {'V', 'R', ' '}


# 5 ---------------------------------------------------------------
def test_5_corredor_e_corredor_1_sao_a_mesma_camera(tmp_path):
    assert normalizar_posicao('Corredor') == normalizar_posicao('Corredor 1') == 'CORREDOR 1'
    assert normalizar_posicao('Câm. Corredor') == 'CORREDOR 1'
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Sheet1'
    ws.append(['Prefixo', 'Nome', 'Data', 'Garagem', 'Problemas Detectados: Câm. Corredor', 'Ações: Câm. Corredor',
               'Problemas Detectados: Câm. Corredor 1', 'Ações: Câm. Corredor 1', 'Observações'])
    ws.append([123, 'Fulano', 'terça-feira, setembro 15, 2026 01:10', 'G', 'Câmera inoperante', 'Ativação da câmera',
               'Sem gravação de imagens', 'Normalização da gravação de imagens', 'Obs'])
    p = tmp_path / 'Revisão_CFTV_teste.xlsx'
    wb.save(p)
    forms, _ = manutencao.processar(p)
    pos = forms[0]['posicoes']
    assert [x['posicao'] for x in pos] == ['CORREDOR 1']  # UMA câmera, nunca "Corredor" + "Corredor 1"
    assert pos[0]['camera'] == 23
    assert pos[0]['problemas'] == ['Câmera inoperante', 'Sem gravação de imagens']  # nada descartado
    assert pos[0]['acoes'] == ['Ativação da câmera', 'Normalização da gravação de imagens']


# 6 ---------------------------------------------------------------
def test_6_manutencao_em_celula_vermelha_mantem_fundo_vermelho_e_marcador(d, df_de):
    regs = [registro(200, d(10), {21: OFF, 22: OK}), registro(200, d(11), {21: OFF, 22: OK}), registro(200, d(15), {21: OK, 22: OK})]
    df = df_de(regs)
    idx, _ = analise.indexar_cftv(df)
    eventos, _ = analise.montar_eventos([form(200, d(11), cams_anomalia=[21])], idx)
    m = exportar.montar_matriz(df, eventos)
    col = {c['data']: i for i, c in enumerate(m['colunas'])}
    item = m['prefixos'][0]
    assert item['g'][col['2026-09-11']] == 'R'  # a cor continua sendo a do CFTV
    assert [eventos[i]['data'] for i in item['m']] == ['2026-09-11']  # marcador (bolinha) na mesma data


# 7 ---------------------------------------------------------------
def test_7_normaliza_e_volta_resolvido_com_recorrencia(d):
    recs = {d(13): registro(1, d(13), {21: OK, 23: OFF}), d(16): registro(1, d(16), {21: OK, 23: OK}),
            d(17): registro(1, d(17), {21: OK, 23: OK}), d(18): registro(1, d(18), {21: OK, 23: OK}),
            d(19): registro(1, d(19), {21: OK, 23: OFF})}
    ev = analise.analisar_evento(1, d(15), [form(1, d(15))], recs, None)
    assert ev['resultado'] == config.RESOLVIDO_REC
    assert ev['antes']['data'] == '2026-09-13'  # 14/09 sem dado não vira OFFLINE
    assert ev['normalizacao']['primeiro_normal'] == '2026-09-16'
    assert ev['permanencia']['registros_normais'] == 3
    assert ev['recorrencia']['data'] == '2026-09-19' and ev['recorrencia']['problemas'][0]['camera'] == 23


def test_7b_problema_em_outra_camera_nao_e_recorrencia(d):
    recs = {d(13): registro(1, d(13), {23: OFF, 25: OK}), d(16): registro(1, d(16), {23: OK, 25: OK}),
            d(17): registro(1, d(17), {23: OK, 25: OFF})}
    ev = analise.analisar_evento(1, d(15), [form(1, d(15))], recs, None)
    assert ev['resultado'] == config.RESOLVIDO
    assert ev['recorrencia'] is None
    assert ev['novo_problema_outra_camera']['problemas'][0]['camera'] == 25
    assert any('Novo problema identificado em outra câmera' in h for h in ev['historia'])


# 8 ---------------------------------------------------------------
def test_8_sem_dado_posterior_sem_dados_para_validar(d):
    recs = {d(22): registro(1, d(22), {21: OFF})}
    ev = analise.analisar_evento(1, d(24), [form(1, d(24))], recs, None)
    assert ev['resultado'] == config.SEM_DADOS
    ev25 = analise.analisar_evento(1, dt.date(2026, 9, 25), [form(1, dt.date(2026, 9, 25))], recs, None)
    assert ev25['resultado'] == config.SEM_DADOS and ev25['fora_periodo']


# ------------------- regras decididas pela usuária -------------------
def test_q2_traco_significa_sem_camera_e_nao_afeta_cor():
    assert interpretar_camera('-')['classificacao'] == 'SEM CÂMERA'
    assert status_geral(cods(OK, '-', '-')) == 'V'
    assert status_geral(cods('-', ERR, '-')) == 'L'


def test_q4_registro_do_dia_nao_conta_como_antes_nem_depois(d):
    recs = {d(10): registro(1, d(10), {21: OFF}), d(11): registro(1, d(11), {21: OK})}
    ev = analise.analisar_evento(1, d(11), [form(1, d(11))], recs, None)
    assert ev['antes']['data'] == '2026-09-10'
    assert ev['dia']['data'] == '2026-09-11'
    assert ev['depois'] == [] and ev['resultado'] == config.SEM_DADOS


def test_q17_veiculo_ja_normal_antes_e_marcador_nao_classe(d):
    recs = {d(10): registro(1, d(10), {21: OK}), d(15): registro(1, d(15), {21: OK})}
    ev = analise.analisar_evento(1, d(11), [form(1, d(11))], recs, None)
    assert ev['veiculo_normal_antes'] is True
    assert ev['resultado'] == config.SEM_DADOS and ev['resultado'] in config.CLASSES


def test_nao_resolvido_e_parcial(d):
    recs = {d(10): registro(1, d(10), {21: OFF, 22: ERR}), d(15): registro(1, d(15), {21: OFF, 22: OK}),
            d(16): registro(1, d(16), {21: OFF, 22: OK})}
    assert analise.analisar_evento(1, d(11), [form(1, d(11))], recs, None)['resultado'] == config.PARCIAL
    recs2 = {d(10): registro(1, d(10), {21: OFF}), d(15): registro(1, d(15), {21: ERR})}
    assert analise.analisar_evento(1, d(11), [form(1, d(11))], recs2, None)['resultado'] == config.NAO_RESOLVIDO


def test_varias_manutencoes_mesmo_dia_um_evento_sem_sobrescrever(d):
    idx = {1: {d(10): registro(1, d(10), {21: OFF}), d(15): registro(1, d(15), {21: OK})}}
    eventos, _ = analise.montar_eventos([form(1, d(11), '01:00', 2), form(1, d(11), '03:00', 3)], idx)
    assert len(eventos) == 1 and eventos[0]['forms'] == [2, 3] and eventos[0]['qtd_formularios'] == 2


def test_texto_livre_cameras_serie_mac_e_data():
    assert manutencao.cameras_no_texto('Troca SD câmera 22 \nTroca da câmera 24') == [22, 24]
    assert manutencao.cameras_no_texto('Câmeras 22 e  23 mal posicionadas; Câmara 21') == [21, 22, 23]
    assert manutencao.notacao_c('C1/C4 FORMATAÇÃO') == ['C1', 'C4']
    eq = manutencao.equipamentos('Número de série câmera instalada \n210235UDL5F247002849\nMAC  E4F14C780CBE\n\nRETIRADA \n\n210A235UGNJ324A003395\nMAC E4F14C7F1524')
    assert eq['instalado'] == {'series': ['210235UDL5F247002849'], 'macs': ['E4F14C780CBE']}
    assert eq['retirado'] == {'series': ['210A235UGNJ324A003395'], 'macs': ['E4F14C7F1524']}
    assert manutencao.parse_data('sexta-feira, setembro 25, 2026 09:40') == dt.datetime(2026, 9, 25, 9, 40)


# Decisão da usuária em 07/10/2026 (§17-A): posições de câmera reconciliadas com o histórico ----------------------
def _reg_completo(prefixo, data, cams):
    r = registro(prefixo, data, cams)
    for n in config.CAMERAS:
        it = interpretar_camera(cams.get(n))
        r[f'cam{n}_original'] = cams.get(n)
        r[f'cam{n}_codigo'] = it['codigo']
        r[f'cam{n}_classificacao'] = it['classificacao']
        r[f'cam{n}_erros'] = ', '.join(it['erros'])
    return r


def test_reconciliacao_cameras_com_historico():
    import pandas as pd
    from cftv import reconciliacao
    antes, novo = dt.date(2026, 9, 24), dt.date(2026, 10, 6)
    regs = [
        _reg_completo(1, antes, {21: OK, 22: '-'}), _reg_completo(1, novo, {21: '-', 22: OFF}),            # 22 -> 21
        _reg_completo(2, antes, {21: OK, 22: OK, 23: '-'}), _reg_completo(2, novo, {21: '-', 22: OK, 23: ERR}),  # 22,23 -> 21,22
        _reg_completo(3, antes, {21: OK, 22: '-'}), _reg_completo(3, novo, {21: OK, 22: OK}),              # 1 × 2: ambíguo
        _reg_completo(4, novo, {21: '-', 22: OK}),                                                          # sem histórico
        _reg_completo(5, dt.date(2026, 9, 1), {21: OK}), _reg_completo(5, antes, {21: '-', 22: OK}),        # antes do corte: não mexe
    ]
    df, rel = reconciliacao.reconciliar(pd.DataFrame(regs))
    g = lambda p, d: df[(df.prefixo == p) & (df.data == d)].iloc[0]
    r1 = g(1, novo)
    assert r1['cam21_original'] == OFF and r1['cam22_original'] == '-' and r1['codigos'][:2] == 'O-'
    assert r1['cameras_reconciliadas'] == 'Câmera 22→21' and r1['status_geral'] == 'R'
    r2 = g(2, novo)
    assert (r2['cam21_original'], r2['cam22_original'], r2['cam23_original']) == (OK, ERR, '-')
    assert g(3, novo)['cam22_original'] == OK and g(3, novo)['cameras_reconciliadas'] is None
    assert g(4, novo)['cam22_original'] == OK
    assert g(5, antes)['cam22_original'] == OK
    assert dict(rel.groupby('acao').size()) == {'REMAPEADO': 2, 'MANTIDO (ambíguo)': 1}
    # nenhum valor criado ou apagado: o multiconjunto de textos de cada registro é o mesmo
    for i, r in enumerate(regs):
        x = df[(df.prefixo == r['prefixo']) & (df.data == r['data'])].iloc[0]
        txt = lambda v: v if isinstance(v, str) else ''
        assert sorted(txt(r[f'cam{n}_original']) for n in config.CAMERAS) == sorted(txt(x[f'cam{n}_original']) for n in config.CAMERAS)

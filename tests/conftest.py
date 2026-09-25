import datetime as dt
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

from cftv.interpretacao import interpretar_camera, status_geral  # noqa: E402

OK = 'ONLINE (SD: ok, Login: ok, Gravação: ok)'
ERR = 'ONLINE (SD: error, Login: ok, Gravação: error)'
OFF = 'OFFLINE'


def registro(prefixo, data, cams, empresa='EMPRESA TESTE', linha=2):
    """cams: dict {21: texto, ...}; câmeras ausentes = célula vazia (fora da grade)."""
    codigos = ''.join(interpretar_camera(cams.get(n))['codigo'] for n in [21, 22, 23, 24, 25, 26])
    return {'prefixo': prefixo, 'data': data, 'empresa': empresa, 'empresa_original': empresa,
            'status_operacional_cftv': 'OK', 'ultima_manutencao_cftv': None, 'arquivo_origem': f'Relatório CFTV - {data:%d.%m.%Y}.xlsx',
            'linha_excel': linha, 'codigos': codigos, 'status_geral': status_geral(codigos)}


def form(prefixo, data, hora='01:00', id_form=2, cams_anomalia=(), pend=False):
    return {'id_form': id_form, 'linha_excel': id_form, 'prefixo': prefixo, 'data': data.isoformat(), 'hora': hora,
            'datahora': f'{data.isoformat()} {hora}', 'tecnico': 'Técnico Teste', 'garagem': 'Garagem Teste',
            'posicoes': [], 'cameras_com_anomalia': list(cams_anomalia), 'cameras_citadas_texto': [],
            'pendencia': pend, 'pendencia_trechos': ([{'trecho': 'PENDENTE', 'termo': 'PENDENTE', 'origem': 'Observações'}] if pend else [])}


@pytest.fixture
def d():
    return lambda dia: dt.date(2026, 9, dia)


@pytest.fixture
def df_de():
    return lambda regs: pd.DataFrame(regs)

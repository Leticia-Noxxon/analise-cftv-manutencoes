"""Configuração central (caminhos, período, mapeamento de câmeras). Ver REGRAS_PROJETO.md §17 (Q3)."""
import datetime as dt
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / 'data' / 'raw'
PROCESSED = RAIZ / 'data' / 'processed'
SITE_DATA = RAIZ / 'site' / 'public' / 'data'

PERIODO_INICIO = dt.date(2026, 9, 1)
PERIODO_FIM = dt.date(2026, 9, 24)

# Mapeamento CONFIRMADO pela usuária em 25/09/2026 (Q3)
CAMERAS = [21, 22, 23, 24, 25, 26]
POSICAO_DA_CAMERA = {21: 'FRONTAL', 22: 'FRENTE', 23: 'CORREDOR 1', 24: 'CORREDOR 2', 25: 'CORREDOR 3', 26: 'CORREDOR 4'}
CAMERA_DA_POSICAO = {v: k for k, v in POSICAO_DA_CAMERA.items()}
ORDEM_POSICOES = ['FRONTAL', 'FRENTE', 'CORREDOR 1', 'CORREDOR 2', 'CORREDOR 3', 'CORREDOR 4']


def rotulo_camera(num: int) -> str:
    """Ex.: 23 -> 'CORREDOR 1 (câm 23)'."""
    return f"{POSICAO_DA_CAMERA.get(num, 'CÂMERA')} (câm {num})"


# Classificações formais (§21) — PENDÊNCIA é marcador separado (Q18)
RESOLVIDO = 'RESOLVIDO'
RESOLVIDO_REC = 'RESOLVIDO COM RECORRÊNCIA'
NAO_RESOLVIDO = 'NÃO RESOLVIDO'
PARCIAL = 'PARCIALMENTE RESOLVIDO'
SEM_DADOS = 'SEM DADOS PARA VALIDAR'
CLASSES = [RESOLVIDO, RESOLVIDO_REC, NAO_RESOLVIDO, PARCIAL, SEM_DADOS]

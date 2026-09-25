"""Interpretação do texto de status das câmeras (§4, §5) e status geral do veículo (§6).

Códigos compactos por câmera (usados no JSON do site e nos testes):
  'N'      ONLINE NORMAL (SD ok, Login ok, Gravação ok)            -> VERDE
  '1'..'7' ONLINE COM ERRO; dígito = máscara de erros (SD=1, Login=2, Gravação=4) -> LARANJA
  'O'      OFFLINE                                                -> VERMELHO
  '-'      SEM CÂMERA (veículo não possui a câmera — decisão Q2)  -> excluída
  '.'      coluna fora da grade da empresa (célula vazia)         -> excluída
  '?'      texto não reconhecido (listado na auditoria, não classificado)
Status geral do dia: 'R' vermelho, 'L' laranja, 'V' verde, 'I' indefinido (só textos '?'), 'S' registro sem câmeras.
"""
import math
import re
import unicodedata

ERRO_BITS = {'SD': 1, 'LOGIN': 2, 'GRAVACAO': 4}
NOMES_ERRO = [(1, 'SD'), (2, 'Login'), (4, 'Gravação')]
_CAMPO = re.compile(r'(SD|Login|Grava[çc][ãa]o)\s*:\s*([A-Za-z]+)', re.IGNORECASE)


def _sem_acento(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def vazio(v) -> bool:
    return v is None or (isinstance(v, float) and math.isnan(v)) or (isinstance(v, str) and v.strip() == '')


def interpretar_camera(valor):
    """Retorna dict com: codigo, classificacao, conectividade, sd, login, gravacao, erros (lista)."""
    base = {'codigo': '?', 'classificacao': 'NÃO RECONHECIDO', 'conectividade': None,
            'sd': None, 'login': None, 'gravacao': None, 'erros': []}
    if vazio(valor):
        return {**base, 'codigo': '.', 'classificacao': 'FORA DA GRADE'}
    s = str(valor).strip()
    if s == '-':
        return {**base, 'codigo': '-', 'classificacao': 'SEM CÂMERA'}
    up = s.upper()
    if up.startswith('OFFLINE'):
        return {**base, 'codigo': 'O', 'classificacao': 'OFFLINE', 'conectividade': 'OFFLINE'}
    if up.startswith('ONLINE'):
        campos = {}
        for nome, val in _CAMPO.findall(s):
            chave = _sem_acento(nome).upper()
            campos[chave] = 'error' if val.lower().startswith('err') else ('ok' if val.lower() == 'ok' else val.lower())
        r = {**base, 'conectividade': 'ONLINE', 'sd': campos.get('SD'), 'login': campos.get('LOGIN'),
             'gravacao': campos.get('GRAVACAO')}
        mask = sum(bit for k, bit in ERRO_BITS.items() if campos.get(k) == 'error')
        if mask:
            r['erros'] = [n for b, n in NOMES_ERRO if mask & b]
            return {**r, 'codigo': str(mask), 'classificacao': 'ONLINE COM ERRO'}
        if all(campos.get(k) == 'ok' for k in ERRO_BITS):
            return {**r, 'codigo': 'N', 'classificacao': 'ONLINE NORMAL'}
        return r  # ONLINE sem os 3 campos 'ok' -> não reconhecido (não se supõe verde)
    return base


def codigo_e_problema(c: str) -> bool:
    return c == 'O' or c.isdigit()


def codigo_existe(c: str) -> bool:
    """Câmera existe e tem informação (entra nas análises)."""
    return c in ('N', 'O', '?') or c.isdigit()


def status_geral(codigos) -> str:
    """Prioridade (§6): OFFLINE > ONLINE COM ERRO > ONLINE NORMAL. '-' e '.' são ignorados (Q2)."""
    cs = [c for c in codigos if codigo_existe(c)]
    if any(c == 'O' for c in cs):
        return 'R'
    if any(c.isdigit() for c in cs):
        return 'L'
    if any(c == '?' for c in cs):
        return 'I'
    if any(c == 'N' for c in cs):
        return 'V'
    return 'S'


NOME_STATUS = {'R': 'VERMELHO', 'L': 'LARANJA', 'V': 'VERDE', 'I': 'INDEFINIDO', 'S': 'SEM CÂMERAS', ' ': 'SEM DADOS'}
DESCR_STATUS = {'R': 'Pelo menos uma câmera OFFLINE', 'L': 'Nenhuma OFFLINE, mas há câmera ONLINE com erro',
                'V': 'Todas as câmeras ONLINE sem erro', 'I': 'Texto de câmera não reconhecido',
                'S': 'Registro sem câmeras instaladas', ' ': 'Sem registro CFTV nesta data'}


def descrever_codigo(c: str) -> str:
    if c == 'N':
        return 'ONLINE'
    if c == 'O':
        return 'OFFLINE'
    if c.isdigit():
        m = int(c)
        return 'ONLINE COM ERRO (' + ', '.join(f'{n}: error' for b, n in NOMES_ERRO if m & b) + ')'
    return {'-': 'SEM CÂMERA', '.': 'FORA DA GRADE', '?': 'NÃO RECONHECIDO'}.get(c, c)


def normalizar_posicao(txt: str):
    """'Corredor' e 'Corredor 1' são a MESMA câmera -> 'CORREDOR 1' (regra obrigatória §3)."""
    if txt is None:
        return None
    t = re.sub(r'\s+', ' ', _sem_acento(str(txt)).upper().strip())
    t = re.sub(r'^(CAM(ERA)?\.?\s*)', '', t)
    if t.startswith('FRONTAL'):
        return 'FRONTAL'
    if t.startswith('FRENTE'):
        return 'FRENTE'
    m = re.match(r'^CORREDOR\s*(\d)?', t)
    if m:
        return f'CORREDOR {m.group(1) or 1}'
    return None

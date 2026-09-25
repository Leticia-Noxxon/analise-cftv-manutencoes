"""Servidor HTTP local (thread) para testar o site compilado (site/dist). Usado por testes e capturas de tela."""
import functools
import http.server
import threading
from pathlib import Path

DIST = Path(__file__).resolve().parents[1] / 'site' / 'dist'


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def iniciar(porta=0):
    if not (DIST / 'index.html').exists():
        raise SystemExit('site/dist não existe: rode "cd site && npm run build" antes.')
    h = functools.partial(_Quiet, directory=str(DIST))
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', porta), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f'http://127.0.0.1:{srv.server_address[1]}/'

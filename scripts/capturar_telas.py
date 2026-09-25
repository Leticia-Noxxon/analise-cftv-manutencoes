"""Captura as telas do painel (docs/screenshots) com navegador headless (Playwright).

Uso:  python scripts/capturar_telas.py      (requer site/dist compilado e `playwright install chromium` ou Chrome)
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from servidor_teste import iniciar  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / 'docs' / 'screenshots'
PREFIXO = '31005'   # exemplo com antes -> manutenção -> depois -> recorrência


def abrir_navegador(p):
    try:
        return p.chromium.launch(channel='chrome')
    except Exception:
        return p.chromium.launch()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    srv, url = iniciar()
    with sync_playwright() as p:
        b = abrir_navegador(p)
        pg = b.new_page(viewport={'width': 1600, 'height': 950}, device_scale_factor=1)
        pg.goto(url)
        pg.wait_for_selector('body[data-pronto="1"]')
        pg.wait_for_selector('.mx-row')
        pg.screenshot(path=OUT / '01_matriz.png')

        pg.fill('#f-busca', PREFIXO)
        pg.wait_for_timeout(400)
        cols = pg.evaluate("() => window.__D.cftv.colunas.map(c => c.data)")
        j_antes = cols.index('2026-09-10')
        cel = pg.locator(f'.c[data-i="0"][data-j="{j_antes}"]')
        cel.hover()
        pg.wait_for_selector('#tooltip:not([hidden])')
        pg.screenshot(path=OUT / '02_tooltip.png')

        cel.click()
        pg.wait_for_selector('#drawer:not([hidden])')
        pg.wait_for_timeout(200)
        pg.screenshot(path=OUT / '03_detalhe_celula.png')
        pg.keyboard.press('Escape')

        pg.locator('.dot').first.click()
        pg.wait_for_selector('#drawer:not([hidden])')
        pg.wait_for_timeout(200)
        pg.screenshot(path=OUT / '04_painel_manutencao.png')
        pg.locator('#drawer .dr-body').evaluate('e => e.scrollTop = 900')
        pg.wait_for_timeout(150)
        pg.screenshot(path=OUT / '04b_painel_manutencao_formulario.png')
        pg.keyboard.press('Escape')

        pg.locator('.pf').first.click()
        pg.wait_for_selector('#drawer:not([hidden])')
        pg.wait_for_timeout(200)
        pg.screenshot(path=OUT / '05_linha_do_tempo.png')
        pg.locator('#drawer .dr-body').evaluate('e => e.scrollTop = e.scrollHeight')
        pg.wait_for_timeout(150)
        pg.screenshot(path=OUT / '05b_linha_do_tempo_eventos.png')
        pg.keyboard.press('Escape')

        pg.fill('#f-busca', '')
        pg.wait_for_timeout(300)
        pg.click('[data-tab="efetividade"]')
        pg.wait_for_timeout(400)
        pg.screenshot(path=OUT / '06_efetividade.png')
        pg.screenshot(path=OUT / '06b_efetividade_completa.png', full_page=True)
        for aba, nome in [('manutencoes', '07_manutencoes'), ('recorrencias', '08_recorrencias'), ('auditoria', '09_auditoria')]:
            pg.click(f'[data-tab="{aba}"]')
            pg.wait_for_timeout(400)
            pg.screenshot(path=OUT / f'{nome}.png')
        pg.click('[data-tab="matriz"]')
        pg.click('[data-veic="todos"]')
        pg.wait_for_timeout(300)
        pg.screenshot(path=OUT / '10_matriz_todos_veiculos.png')
        b.close()
    srv.shutdown()
    print('Telas salvas em', OUT)
    for f in sorted(OUT.glob('*.png')):
        print(' ', f.name)


if __name__ == '__main__':
    main()

"""Fase 1-2: lista abas, dimensões, cabeçalhos e primeiras linhas de cada arquivo em data/raw (somente leitura)."""
import glob, os, openpyxl
RAW = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw')
for f in sorted(glob.glob(os.path.join(RAW, '*.xlsx'))):
    wb = openpyxl.load_workbook(f, read_only=False, data_only=True)
    print('=' * 100)
    print(os.path.basename(f))
    for ws in wb.worksheets:
        print(f'  ABA: {ws.title!r} dims={ws.dimensions} max_row={ws.max_row} max_col={ws.max_column} state={ws.sheet_state}')
        pivots = getattr(ws, '_pivots', [])
        if pivots: print(f'    pivot tables: {len(pivots)}')
        if ws.tables: print(f'    tables: {list(ws.tables.keys())}')
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i >= 5: break
            print('    ', row)

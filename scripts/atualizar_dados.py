"""COMO ATUALIZAR OS DADOS: coloque os novos 'Relatório CFTV - DD.MM.AAAA.xlsx' e/ou o novo 'Revisão_CFTV*.xlsx'
em data/raw/ e execute:   python scripts/atualizar_dados.py
Gera data/processed/* (bases tratadas CSV/XLSX) e site/public/data/*.json (dados do dashboard).
Nenhum arquivo de data/raw é alterado."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cftv import analise, config, exportar, leitura_cftv, manutencao, reconciliacao  # noqa: E402


def main():
    t0 = time.time()
    print('1/4 Lendo e consolidando Relatórios CFTV...')
    df, infos = leitura_cftv.consolidar()
    for i in infos:
        print(f"   {i['arquivo']}: aba '{i['aba_utilizada']}' ({i['registros']} registros); ignoradas: {[x['aba'] for x in i['abas_ignoradas']]}")
    print(f'   total: {len(df)} registros, {df.prefixo.nunique()} prefixos')
    df, reconc = reconciliacao.reconciliar(df)
    if len(reconc):
        from collections import Counter as _C
        print(f"   reconciliação de câmeras com o histórico (a partir de {config.RECONCILIAR_A_PARTIR:%d/%m/%Y}):",
              dict(_C(reconc['acao'])))
    # período: 01/09–24/09/2026 por padrão; amplia automaticamente se chegarem arquivos de outras datas
    import pandas as pd
    dmin, dmax = pd.to_datetime(df['data']).min().date(), pd.to_datetime(df['data']).max().date()
    config.PERIODO_INICIO = min(config.PERIODO_INICIO, dmin)
    config.PERIODO_FIM = max(config.PERIODO_FIM, dmax)
    print(f'   período analisado: {config.PERIODO_INICIO:%d/%m/%Y} a {config.PERIODO_FIM:%d/%m/%Y}')
    print('2/4 Processando formulário de manutenção...')
    forms, finfo = manutencao.processar(prefixos_cftv=set(df['prefixo']))
    print(f"   {finfo['arquivo']}: {len(forms)} formulários")
    print('3/4 Relacionando manutenção × CFTV (antes/depois/recorrência)...')
    idx, dup = analise.indexar_cftv(df)
    eventos, sem_data = analise.montar_eventos(forms, idx)
    from collections import Counter
    print('   ', dict(Counter(e['resultado'] for e in eventos)))
    print('4/4 Gerando bases tratadas e dados do site...')
    exportar.gerar(df, infos, forms, finfo, eventos, dup, sem_data, reconc)
    print(f'Concluído em {time.time() - t0:.0f}s. Saídas: {config.PROCESSED} e {config.SITE_DATA}')


if __name__ == '__main__':
    main()

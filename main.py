import logging
import pandas as pd
from datetime import datetime
from argparse import ArgumentParser

from orquestrador import IssueService

def replace_bool(param: bool) -> str:
    if param:
        return 'Sim'
    return 'Não'

if __name__ == '__main__':
    parser = ArgumentParser(description='Importa issues para o GitHub a partir de um CSV exportado do GitLab.')

    parser.add_argument('csv_file', type=str, help='caminho CSV exportado do gitlab')
    parser.add_argument('--create_milestones', action='store_true', help='Flag para a criação de Milestones baseado no CSV')
    parser.add_argument('--milestones', action='store_true', help='Importação de Milestones')
    parser.add_argument('--assignees', action='store_true', help='Importação de assignees')
    
    args = parser.parse_args()

    logging.basicConfig(
        filename=f'LOG_{datetime.now().strftime("%Y-%m-%d")}.log',
        filemode="a",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)
    logger.info(''.join((
        'Iniciando importação de issues...',
        f'\n\tArquivo: {args.csv_file}',
        f'\n\tCriar Milestones? {replace_bool(args.create_milestones)}',
        f'\n\tImportar Milestones? {replace_bool(args.milestones)}',
        f'\n\tImportar responsáveis? {replace_bool(args.assignees)}',
    )))

    df = pd.read_csv(args.csv_file)
    issue_service = IssueService()
    if args.create_milestones:
        issue_service.create_milestones(df=df)
    issue_service.create_issues(df=df, add_assignees=args.assignees, add_milestones=args.milestones)

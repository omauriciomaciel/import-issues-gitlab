import pandas as pd
from argparse import ArgumentParser

from orquestrador import IssueService


if __name__ == '__main__':
    parser = ArgumentParser(description='Importa issues para o GitHub a partir de um CSV exportado do GitLab.')

    parser.add_argument('csv_file', type=str, help='caminho CSV exportado do gitlab')
    parser.add_argument('--create_milestones', action='store_true', help='Flag para a criação de Milestones baseado no CSV')
    parser.add_argument('--milestones', action='store_true', help='Importação de Milestones')
    parser.add_argument('--assignees', action='store_true', help='Importação de assignees')
    
    args = parser.parse_args()

    df = pd.read_csv(args.csv_file)
    issue_service = IssueService()
    if args.create_milestones:
        issue_service.create_milestones(df=df)
    issue_service.create_issues(df=df, add_assignees=args.assignees, add_milestones=args.milestones)

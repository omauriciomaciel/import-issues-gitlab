import os
import re
import json
import time
from pandas import DataFrame
from pydantic import BaseModel
from typing import List, Dict
from dotenv import load_dotenv

from client import GithubClient

load_dotenv()

class GithubDataModel(BaseModel):
    number: int
    state: str
    title: str


class IssueService:
    def __init__(self):
        credentials = {
            'token': os.getenv('TOKEN'),
            'owner': os.getenv('OWNER'),
            'repo': os.getenv('REPO'),
        }
        self.gclient = GithubClient(**credentials)

    def get_milestones(self) -> List[GithubDataModel]:
        milestones = self.gclient.get('milestones')
        milestones = [{
            key: value for key,value in item.items() if key in ('number', 'state', 'title')
        } for item in milestones]
        return milestones

    def get_issues(self, params: None| Dict = None) -> List[GithubDataModel]:
        issues = self.gclient.get('issues', params)
        issues = [{
            key: value for key,value in item.items() if key in ('number', 'state', 'title')
        } for item in issues]
        return issues

    def create_milestones(self, df: DataFrame) -> List[GithubDataModel]:
        milestones_df = list(df["Milestone"].dropna().unique())
        new_milestones = list()
        for milestone_title in milestones_df:
            data = {'title': milestone_title}
            milestone = self.gclient.post('milestones', data=data)
            new_milestones.append({
                key: value for key,value in milestone.items() if key in ('number', 'state', 'title')
            })
            time.sleep(1)
        return new_milestones

    def create_issues(self, df: DataFrame, add_assignees=False, add_milestones=False) -> List:
        df = df.fillna('')
        issues = self.get_issues({'sort': 'created', 'direction': 'desc'})
        last_issue = issues[0] if issues else 0
        if add_milestones:
            milestones = self.get_milestones()
        df = df.sort_values(by='IID')
        assignees_map = self._map_assignees()
        for idx, row in df.iterrows():
            data = {
                'title': row['Title'],
                'body': self._handle_issue_body(row['Description'], last_issue),
            }
            labels = self._handle_labels(row['Labels'])
            if labels:
                data['labels'] = labels

            assignees = self._handle_assignees(row['Assignee Username'], assignees_map)
            if add_assignees and assignees:
                data['assignees'] = [assignees]

            if add_milestones:
                milestone = self._handle_milestone(row['Milestone'], milestones)
                if milestone:
                    data['milestone'] = milestone

            self.gclient.post(
                'issues', data=data
            )
            time.sleep(1)

    @staticmethod
    def _handle_issue_body(text: str, max_issues: int) -> str:
        def replace_issue_number(match):
            old_number = int(match.group(1))
            return f'#{max_issues + old_number}'
        
        return re.sub(r'#(\d+)', replace_issue_number, text)

    @staticmethod
    def _handle_labels(labels: str) -> List[str]:
        if not labels:
            return
        labels = [lbl.strip() for lbl in labels.split(',')]
        return labels
    
    @staticmethod
    def _map_assignees() -> Dict[str, str] | None:
        if not os.path.exists('assignees_map.json'):
            return
        with open('assignees_map.json', 'r') as f:
            data = json.load(f)
        return data

    @staticmethod
    def _handle_assignees(text: str, assignees_map: Dict[str, str]) -> str | None:
        if not assignees_map or not text:
            return
        return assignees_map.get(text.strip(), None)
    
    @staticmethod
    def _handle_milestone(text: str, milestones: List) -> int | None:
        if not text:
            return
        for number, state, title in [m.values() for m in milestones]:
            if text.lower().strip() == title.lower().strip():
                return number
        return


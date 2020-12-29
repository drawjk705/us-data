from api import ApiConfig
from typing import Dict, List
from api.utils import getData_Base
from api.models import Group


def fetchGroupData(apiConfig: ApiConfig) -> Dict[str, Group]:
    groupsRes: Dict[str, List[Dict[str, str]]] = getData_Base(
        apiConfig, route='/groups.json')

    return __parseGroups(groupsRes)


def __parseGroups(groupsRes: Dict[str, List[Dict[str, str]]]) -> Dict[str, Group]:
    return {Group(group).name: Group(group) for group in groupsRes['groups']}

from api.ApiConfig import ApiConfig
from typing import Dict, List
from api.getData_Base import getData_Base
from api.models.Group import Group


def getGroupData(apiConfig: ApiConfig) -> Dict[str, Group]:
    groupsRes: Dict[str, List[Dict[str, str]]] = getData_Base(
        apiConfig, route='/groups.json')

    return __parseGroups(groupsRes)


def __parseGroups(groupsRes: Dict[str, List[Dict[str, str]]]) -> Dict[str, Group]:
    return {Group(group).name: Group(group) for group in groupsRes['groups']}

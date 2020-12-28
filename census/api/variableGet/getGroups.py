from typing import Dict
from api.getData_Base import getData_Base
from models import DatasetType, SurveyType
from api.models.Group import Group


def getGroups(year: int,
              datasetType: DatasetType = DatasetType.ACS,
              surveyType: SurveyType = SurveyType.ACS1) -> Dict[str, Group]:
    groupsRes: Dict[str, Dict[str, str]] = getData_Base(
        year, datasetType=datasetType, surveyType=surveyType, route='/groups.json')

    return __parseGroups(groupsRes)


def __parseGroups(groupsRes: Dict[str, Dict[str, str]]) -> Dict[str, Group]:
    return {Group(group).name: Group(group) for group in groupsRes['groups']}

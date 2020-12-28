from api.models.GroupVariable import GroupVariable
from models.SurveyType import SurveyType
from models.DatasetType import DatasetType
from api.getData_Base import getData_Base
from typing import Any, List


def getVariableData(group: str,
                    year: int,
                    datasetType: DatasetType = DatasetType.ACS,
                    surveyType: SurveyType = SurveyType.ACS1) -> List[GroupVariable]:
    res = getData_Base(year, datasetType=datasetType,
                       surveyType=surveyType, route=f'/groups/{group}.json')

    return __parseVariableData(res)


def __parseVariableData(variableData: Any) -> List[GroupVariable]:
    variables = []
    for varCode, varData in variableData['variables'].items():
        groupVar = GroupVariable(code=varCode, jsonData=varData)
        variables.append(groupVar)

    return variables

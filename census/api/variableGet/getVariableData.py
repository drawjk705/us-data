from api.ApiConfig import ApiConfig
from api.models.GroupVariable import GroupVariable
from api.getData_Base import getData_Base
from typing import Any, List


def getVariableData(group: str, apiConfig: ApiConfig) -> List[GroupVariable]:
    res = getData_Base(apiConfig, route=f'/groups/{group}.json')

    return __parseVariableData(res)


def __parseVariableData(variableData: Any) -> List[GroupVariable]:
    variables = []
    for varCode, varData in variableData['variables'].items():
        groupVar = GroupVariable(code=varCode, jsonData=varData)
        variables.append(groupVar)

    return variables

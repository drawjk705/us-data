from api.ApiConfig import ApiConfig
from api.models.GroupVariable import GroupVariable
from api.utils import fetchData_Base
from typing import Any, List


def fetchVariableData(group: str, apiConfig: ApiConfig) -> List[GroupVariable]:
    res = fetchData_Base(apiConfig, route=f'/groups/{group}.json')

    return __parseVariableData(res)


def __parseVariableData(variableData: Any) -> List[GroupVariable]:
    variables = []
    for varCode, varData in variableData['variables'].items():
        groupVar = GroupVariable(code=varCode, jsonData=varData)
        variables.append(groupVar)

    return variables

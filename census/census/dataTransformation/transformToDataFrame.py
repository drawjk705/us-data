from census.dataTransformation.interface import IDataTransformer
from collections import OrderedDict
from typing import Dict, List, Type, Union

import pandas as pd
from census.api.models import GeographyItem
from census.api.models import Group, GroupVariable


class DataFrameTransformer(IDataTransformer[pd.DataFrame]):
    def __init__(self) -> None:
        super().__init__()

    def supportedGeographies(
        self, supportedGeos: OrderedDict[str, GeographyItem]
    ) -> pd.DataFrame:
        valuesFlattened: List[Dict[str, str]] = []
        for geoItem in supportedGeos.values():
            for clause in geoItem.clauses:
                valuesFlattened.append(
                    {
                        "name": geoItem.name,
                        "hierarchy": geoItem.hierarchy,
                        "for": clause.forClause,
                        "in": ",".join(clause.inClauses),
                    }
                )

        return pd.DataFrame(valuesFlattened)

    def geographyCodes(self, geoCodes: List[List[str]]) -> pd.DataFrame:
        return pd.DataFrame(geoCodes[1:], columns=geoCodes[0])

    def groups(self, groups: Dict[str, Group]) -> pd.DataFrame:
        groupsList = []
        for code, groupObj in groups.items():
            groupDict = {"code": code, "description": groupObj.description}
            groupsList.append(groupDict)

        return pd.DataFrame(groupsList)

    def variables(self, variables: List[GroupVariable]) -> pd.DataFrame:
        variableDictList: List[Dict[str, Union[str, int, bool]]] = []

        for variable in variables:
            variableDictList.append(
                {
                    "code": variable.code,
                    "groupCode": variable.groupCode,
                    "concept": variable.groupConcept,
                    "name": variable.name,
                    "limit": variable.limit,
                    "predicateOnly": variable.predicateOnly,
                    "predicateType": variable.predicateType,
                }
            )

        return pd.DataFrame(variableDictList)

    def stats(
        self, results: List[List[str]], queriedVariables: List[GroupVariable]
    ) -> pd.DataFrame:
        df = pd.DataFrame(results[1:], columns=results[0])

        columnsList = df.columns.tolist()
        columnsSet = set(columnsList)
        # just as as precaution
        relevantVariables = [qv for qv in queriedVariables if qv.code in columnsSet]

        if len(relevantVariables) < len(queriedVariables):
            raise Exception("Could not match all variables")

        # convert columns to proper data types
        variableToDataType: Dict[str, Union[Type[int], Type[float]]] = {}

        for variable in relevantVariables:
            code = variable.code
            dataType = variable.predicateType

            if dataType == "int":
                variableToDataType.update({code: int})
            elif dataType == "float":
                variableToDataType.update({code: float})

        df = df.astype(variableToDataType)  # type: ignore

        # reshuffle the columns
        nameCol = columnsList[0]
        variableCols = columnsList[1 : len(queriedVariables) + 1]
        geoCols = columnsList[1 + len(queriedVariables) :]

        reorderedColumns = [nameCol] + geoCols + variableCols

        return df[reorderedColumns]

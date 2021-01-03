from census.utils.timer import timer
from census.variables.models import Group, GroupVariable, VariableCode
from census.dataTransformation.interface import IDataTransformer
from collections import OrderedDict
from typing import Any, Dict, List, Union

import pandas as pd
from census.api.models import GeographyItem


class DataFrameTransformer(IDataTransformer[pd.DataFrame]):
    def __init__(self) -> None:
        super().__init__()

    @timer
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

    @timer
    def geographyCodes(self, geoCodes: List[List[str]]) -> pd.DataFrame:
        return pd.DataFrame(geoCodes[1:], columns=geoCodes[0]).sort_values(by=["state"])

    @timer
    def groups(self, groups: Dict[str, Group]) -> pd.DataFrame:
        groupsList = []
        for code, groupObj in groups.items():
            groupDict = {"code": code, "description": groupObj.description}
            groupsList.append(groupDict)

        return pd.DataFrame(groupsList).sort_values(by="code")

    @timer
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

        return pd.DataFrame(variableDictList).sort_values(by=["code"])

    @timer
    def stats(
        self,
        results: List[List[Any]],
        queriedVariables: List[VariableCode],
        typeConversions: Dict[str, Any],
    ) -> pd.DataFrame:
        df = pd.DataFrame(results[1:], columns=results[0])

        columnsList = df.columns.tolist()

        # reshuffle the columns
        nameCol = columnsList[0]
        variableCols = columnsList[1 : len(queriedVariables) + 1]
        geoCols = columnsList[1 + len(queriedVariables) :]

        reorderedColumns = [nameCol] + geoCols + variableCols

        return df[reorderedColumns].astype(typeConversions)

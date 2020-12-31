from census.dataTransformation.IDataTransformer import IDataTransformer
from collections import OrderedDict
from typing import Dict, List, Union

import pandas as pd
from census.api.models import GeographyItem
from census.api.models import Group, GroupVariable


class DataFrameTransformer(IDataTransformer[pd.DataFrame]):
    def __init__(self) -> None:
        pass

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

    def groupData(self, groups: Dict[str, Group]) -> pd.DataFrame:
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

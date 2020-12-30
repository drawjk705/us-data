from collections import OrderedDict
from typing import Dict, List

import pandas as pd
from census.api.models import GeographyItem
from census.api.models import Group, GroupVariable


def supportedGeographies(
    supportedGeos: OrderedDict[str, GeographyItem]
) -> pd.DataFrame:
    valuesFlattened = []
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


def geographyCodes(geoCodes: List[List[str]]) -> pd.DataFrame:
    return pd.DataFrame(geoCodes[1:], columns=geoCodes[0])


def groupData(groupData: Dict[str, Group]) -> pd.DataFrame:
    groupsList = []
    for code, groupObj in groupData.items():
        groupDict = {"code": code, "description": groupObj.description}
        groupsList.append(groupDict)

    return pd.DataFrame(groupsList)


def variables(variables: List[GroupVariable]) -> pd.DataFrame:
    variableDictList: List[Dict] = []  # type: ignore

    for variable in variables:
        variableDictList.append(  # type: ignore
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

    return pd.DataFrame(variableDictList)  # type: ignore

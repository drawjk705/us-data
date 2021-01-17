from collections import OrderedDict
from typing import Any, Dict, List, Optional, Union, cast

import pandas as pd

from the_census._api.models import GeographyItem
from the_census._dataTransformation.interface import ICensusDataTransformer
from the_census._geographies.models import GeoDomain
from the_census._utils.timer import timer
from the_census._variables.models import Group, GroupVariable, VariableCode


class CensusDataTransformer(ICensusDataTransformer[pd.DataFrame]):
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
        return (
            pd.DataFrame(geoCodes[1:], columns=geoCodes[0])
            .sort_values(by=geoCodes[0][1:])
            .reset_index(drop=True)
        )

    @timer
    def groups(self, groups: Dict[str, Group]) -> pd.DataFrame:
        groupsList = []
        for code, groupObj in groups.items():
            groupDict = {
                "code": code,
                "description": groupObj.description,
                "cleanedName": groupObj.cleanedName,
            }
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
                    "groupConcept": variable.groupConcept,
                    "name": variable.name,
                    "predicateType": variable.predicateType,
                    "predicateOnly": variable.predicateOnly,
                    "limit": variable.limit,
                    "cleanedName": variable.cleanedName,
                }
            )

        return (
            pd.DataFrame(variableDictList)
            .sort_values(by=["code"])
            .reset_index(drop=True)
        )

    @timer
    def stats(
        self,
        results: List[List[List[str]]],
        typeConversions: Dict[str, Any],
        geoDomains: List[GeoDomain],
        columnHeaders: Optional[Dict[VariableCode, str]],
    ) -> pd.DataFrame:
        mainDf = pd.DataFrame()
        geoCols = [geoDomain.name for geoDomain in geoDomains]

        for result in results:
            df = pd.DataFrame(result[1:], columns=result[0])

            if mainDf.empty:  # type: ignore
                mainDf = df
            else:
                df = df.drop(columns=["NAME"])  # type: ignore
                mainDf = pd.merge(mainDf, df, on=geoCols, how="inner")  # type: ignore

        allCols = cast(List[str], mainDf.columns.tolist())  # type: ignore

        # reshuffle the columns
        nameCol = ["NAME"]
        variableCols = [col for col in allCols if col != "NAME" and col not in geoCols]

        reorderedColumns = nameCol + geoCols + variableCols

        return (
            mainDf[reorderedColumns]  # type: ignore
            .astype(typeConversions)
            .rename(columns=columnHeaders or {})
            .sort_values(by=geoCols)
            .reset_index(drop=True)
        )

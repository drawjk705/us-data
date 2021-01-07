from census.models import GeoDomain
from census.utils.timer import timer
from census.variables.models import Group, GroupVariable, VariableCode
from census.dataTransformation.interface import IDataTransformer
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from census.api.models import GeographyItem


# pyright: reportUnknownMemberType=false
# pyright: reportGeneralTypeIssues=false


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
        return (
            pd.DataFrame(geoCodes[1:], columns=geoCodes[0])
            .sort_values(by=geoCodes[0][1:])
            .reset_index(drop=True)
        )

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
                    "groupConcept": variable.groupConcept,
                    "name": variable.name,
                    "predicateType": variable.predicateType,
                    "predicateOnly": variable.predicateOnly,
                    "limit": variable.limit,
                }
            )

        return pd.DataFrame(variableDictList).sort_values(by=["code"])

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

            if mainDf.empty:
                mainDf = df
            else:
                mainDf = pd.merge(mainDf, df, on=geoCols, how="inner")  # type: ignore
                mainDf = mainDf.drop(columns=["NAME_x"]).rename(  # type: ignore
                    columns=dict(NAME_y="NAME")
                )

        allCols = mainDf.columns.tolist()  # type: ignore

        # reshuffle the columns
        nameCol = ["NAME"]
        variableCols = [col for col in allCols if col != "NAME" and col not in geoCols]  # type: ignore

        reorderedColumns = nameCol + geoCols + variableCols

        return (  # type: ignore
            mainDf[reorderedColumns]
            .astype(typeConversions)
            .rename(columns=columnHeaders or {})
            .sort_values(by=geoCols)
            .reset_index(drop=True)
        )

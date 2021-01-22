from collections import OrderedDict
from typing import Any, Dict, List, Tuple, Union, cast

import pandas as pd

from the_census._api.models import GeographyItem
from the_census._config import Config
from the_census._dataTransformation.interface import ICensusDataTransformer
from the_census._geographies.interface import IGeographyRepository
from the_census._geographies.models import GeoDomain
from the_census._utils.timer import timer
from the_census._variables.models import Group, GroupVariable, VariableCode


class CensusDataTransformer(ICensusDataTransformer[pd.DataFrame]):

    _geoRepo: IGeographyRepository[pd.DataFrame]
    _config: Config

    def __init__(
        self, geoRepo: IGeographyRepository[pd.DataFrame], config: Config
    ) -> None:
        self._geoRepo = geoRepo
        self._config = config

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
        geoDomainsQueried: List[GeoDomain],
        columnHeaders: Dict[VariableCode, str],
    ) -> pd.DataFrame:
        mainDf = pd.DataFrame()

        mergeKeys = [domain.name for domain in geoDomainsQueried]

        for result in results:
            df = pd.DataFrame(result[1:], columns=result[0])

            if mainDf.empty:
                mainDf = df
            else:
                df = df.drop(columns=["NAME"])  # type: ignore
                mainDf = cast(pd.DataFrame, pd.merge(mainDf, df, on=mergeKeys, how="inner"))  # type: ignore

        allCols = mainDf.columns.tolist()

        nameCol, sortedGeoCols, variableCols = self._partitionStatColumns(
            columnHeaders, allCols
        )

        reorderedColumns = nameCol + sortedGeoCols + variableCols

        return (
            mainDf[reorderedColumns]  # type: ignore
            .astype(typeConversions)
            .rename(columns=columnHeaders if self._config.replaceColumnHeaders else {})
            .sort_values(by=sortedGeoCols)
            .reset_index(drop=True)
        )

    def _partitionStatColumns(
        self, renamedColumnHeaders: Dict[VariableCode, str], dfColumns: List[str]
    ) -> Tuple[List[str], List[str], List[str]]:
        originalVariableHeaders = [str(col) for col in renamedColumnHeaders.keys()]
        nameHeader = ["NAME"]

        geoCols = [
            col for col in dfColumns if col not in nameHeader + originalVariableHeaders
        ]
        sortedGeoCols = [
            domain.name
            for domain in self._sortGeoDomains([GeoDomain(col) for col in geoCols])
        ]

        variableCols = [
            col for col in dfColumns if col != "NAME" and col not in geoCols
        ]

        return nameHeader, sortedGeoCols, variableCols

    def _sortGeoDomains(self, geoDomains: List[GeoDomain]) -> List[GeoDomain]:
        supportedGeos = self._geoRepo.getSupportedGeographies()
        geoHierarchyMapping: List[Dict[str, str]] = (
            supportedGeos[["name", "hierarchy"]].drop_duplicates().to_dict("records")
        )
        geoNameToHierarchy = {
            mapping["name"]: mapping["hierarchy"] for mapping in geoHierarchyMapping
        }

        return sorted(
            geoDomains, key=lambda geoDomain: geoNameToHierarchy[geoDomain.name]
        )

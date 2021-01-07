from census.geographies.interface import IGeographyRepository
from census.config import Config
from census.utils.cleanVariableName import cleanVariableName
from census.utils.timer import timer
from census.variables.repository.interface import IVariableRepository
from census.variables.models import VariableCode
from census.utils.unique import getUnique
from functools import cache
from typing import Any, Dict, List, Set, Tuple
from tqdm.notebook import tqdm

import pandas as pd
from census.api.interface import IApiFetchService
from census.dataTransformation.interface import IDataTransformer
from census.models import GeoDomain
from census.stats.interface import ICensusStatisticsService


class CensusStatisticsService(ICensusStatisticsService[pd.DataFrame]):
    _api: IApiFetchService
    _transformer: IDataTransformer[pd.DataFrame]
    _variableRepo: IVariableRepository[pd.DataFrame]
    _geoRepo: IGeographyRepository[pd.DataFrame]
    _config: Config

    def __init__(
        self,
        api: IApiFetchService,
        transformer: IDataTransformer[pd.DataFrame],
        variableRepo: IVariableRepository[pd.DataFrame],
        geoRepo: IGeographyRepository[pd.DataFrame],
        config: Config,
    ) -> None:
        self._api = api
        self._transformer = transformer
        self._variableRepo = variableRepo
        self._config = config
        self._geoRepo = geoRepo

    @timer
    def getStats(
        self,
        variablesToQuery: List[VariableCode],
        forDomain: GeoDomain,
        *inDomains: GeoDomain,
    ) -> pd.DataFrame:

        return self.__getStats(
            variablesToQuery=tuple(getUnique(variablesToQuery)),
            forDomain=forDomain,
            inDomains=tuple(getUnique(inDomains)),
        )

    @cache
    def __getStats(
        self,
        variablesToQuery: Tuple[VariableCode],
        forDomain: GeoDomain,
        inDomains: Tuple[GeoDomain],
    ) -> pd.DataFrame:

        pullStats = lambda: self._api.stats(
            list(variablesToQuery), forDomain, list(inDomains)
        )

        apiResults: List[List[List[str]]] = [res for res in tqdm(pullStats())]  # type: ignore

        columnHeaders, typeConversions = self._getVariableNamesAndTypeConversions(
            set(variablesToQuery)
        )

        sortedGeoDomains = self._sortGeoDomains([forDomain] + list(inDomains))

        df = self._transformer.stats(
            apiResults,
            typeConversions,
            sortedGeoDomains,
            columnHeaders=columnHeaders if self._config.replaceColumnHeaders else None,
        )

        return df

    def _getVariableNamesAndTypeConversions(
        self, variablesToQuery: Set[VariableCode]
    ) -> Tuple[Dict[VariableCode, str], Dict[str, Any]]:
        relevantVariables = {
            variable.code: variable
            for variable in self._variableRepo.variables.values()
            if variable.code in variablesToQuery
        }
        hasDuplicateNames = len({v.name for v in relevantVariables.values()}) < len(
            variablesToQuery
        )

        typeConversions: Dict[str, Any] = {}
        columnHeaders: Dict[VariableCode, str] = {}
        for k, v in relevantVariables.items():
            if v.predicateType == "float":
                typeConversions.update({k: float})
            elif v.predicateType == "int":
                typeConversions.update(  # this is so we don't get errors when int-type fields are null
                    {k: float}
                )

            cleanedVarName = cleanVariableName(v.name)
            if hasDuplicateNames:
                cleanedVarName += f"_{v.groupCode}"

            columnHeaders.update({k: cleanedVarName})

        return columnHeaders, typeConversions

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

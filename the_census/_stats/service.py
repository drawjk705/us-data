from functools import cache
from logging import Logger
from typing import Any, Dict, List, Set, Tuple

import pandas as pd

from the_census._api.interface import ICensusApiFetchService
from the_census._config import Config
from the_census._dataTransformation.interface import ICensusDataTransformer
from the_census._exceptions import EmptyRepositoryException
from the_census._geographies.interface import IGeographyRepository
from the_census._geographies.models import GeoDomain
from the_census._stats.interface import ICensusStatisticsService
from the_census._utils.log.factory import ILoggerFactory
from the_census._utils.timer import timer
from the_census._utils.unique import getUnique
from the_census._variables.models import VariableCode
from the_census._variables.repository.interface import IVariableRepository


class CensusStatisticsService(ICensusStatisticsService[pd.DataFrame]):
    _api: ICensusApiFetchService
    _transformer: ICensusDataTransformer[pd.DataFrame]
    _variableRepo: IVariableRepository[pd.DataFrame]
    _geoRepo: IGeographyRepository[pd.DataFrame]
    _config: Config
    _logger: Logger

    def __init__(
        self,
        api: ICensusApiFetchService,
        transformer: ICensusDataTransformer[pd.DataFrame],
        variableRepo: IVariableRepository[pd.DataFrame],
        geoRepo: IGeographyRepository[pd.DataFrame],
        config: Config,
        loggerFactory: ILoggerFactory,
    ) -> None:
        self._api = api
        self._transformer = transformer
        self._variableRepo = variableRepo
        self._config = config
        self._geoRepo = geoRepo
        self._logger = loggerFactory.getLogger(__name__)

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

        apiResults: List[List[List[str]]] = [res for res in pullStats()]

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
        if len(relevantVariables) != len(variablesToQuery):
            msg = f"Queried {len(variablesToQuery)} variables, but found only {len(relevantVariables)} in repository"

            self._logger.exception(msg)

            raise EmptyRepositoryException(msg)

        hasDuplicateNames = len(
            {v.cleanedName for v in relevantVariables.values()}
        ) < len(variablesToQuery)

        typeConversions: Dict[str, Any] = {}
        columnHeaders: Dict[VariableCode, str] = {}
        for k, v in relevantVariables.items():
            if v.predicateType in ["int", "float"]:
                typeConversions.update({k: float})

            cleanedVarName = v.cleanedName
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

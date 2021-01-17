from typing import List

import pandas as pd

from the_census._api.fetch import ICensusApiFetchService
from the_census._geographies.interface import IGeographyRepository
from the_census._geographies.models import GeoDomain, SupportedGeoSet
from the_census._stats.interface import ICensusStatisticsService
from the_census._variables.models import GroupCode, VariableCode
from the_census._variables.repository.interface import IVariableRepository
from the_census._variables.repository.models import GroupSet, VariableSet
from the_census._variables.search.interface import IVariableSearchService


class CensusClient:
    """
    The Census client. Using a layer of indirection to hide
    additional properties from consumers.
    """

    _variableRepo: IVariableRepository[pd.DataFrame]
    _variableSearch: IVariableSearchService[pd.DataFrame]
    _stats: ICensusStatisticsService[pd.DataFrame]
    _geoRepo: IGeographyRepository[pd.DataFrame]

    def __init__(
        self,
        variableRepo: IVariableRepository[pd.DataFrame],
        variableSearch: IVariableSearchService[pd.DataFrame],
        stats: ICensusStatisticsService[pd.DataFrame],
        api: ICensusApiFetchService,
        geoRepo: IGeographyRepository[pd.DataFrame],
    ) -> None:
        self._variableRepo = variableRepo
        self._variableSearch = variableSearch
        self._stats = stats
        self._geoRepo = geoRepo

        # if this healthcheck fails, it will throw, and we
        # won't instantiate the client
        api.healthCheck()

    # search
    def searchGroups(self, regex: str) -> pd.DataFrame:
        return self._variableSearch.searchGroups(regex).copy(deep=True)

    def searchVariables(
        self,
        regex: str,
        *inGroups: GroupCode,
    ) -> pd.DataFrame:
        return self._variableSearch.searchVariables(regex, *inGroups).copy(deep=True)

    # repo
    def getGeographyCodes(
        self, forDomain: GeoDomain, *inDomains: GeoDomain
    ) -> pd.DataFrame:
        return self._geoRepo.getGeographyCodes(forDomain, *inDomains).copy(deep=True)

    def getGroups(self) -> pd.DataFrame:
        return self._variableRepo.getGroups().copy(deep=True)

    def getVariablesByGroup(self, *groups: GroupCode) -> pd.DataFrame:
        return self._variableRepo.getVariablesByGroup(*groups).copy(deep=True)

    def getAllVariables(self) -> pd.DataFrame:
        return self._variableRepo.getAllVariables().copy(deep=True)

    def getSupportedGeographies(self) -> pd.DataFrame:
        return self._geoRepo.getSupportedGeographies().copy(deep=True)

    def getStats(
        self,
        variablesToQuery: List[VariableCode],
        forDomain: GeoDomain,
        *inDomains: GeoDomain,
    ) -> pd.DataFrame:
        return self._stats.getStats(variablesToQuery, forDomain, *inDomains).copy(
            deep=True
        )

    # property variables for Jupyter notebook usage

    @property
    def variables(self) -> VariableSet:
        return self._variableRepo.variables

    @property
    def groups(self) -> GroupSet:
        return self._variableRepo.groups

    @property
    def supportedGeographies(self) -> SupportedGeoSet:
        return self._geoRepo.supportedGeographies

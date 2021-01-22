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
        api.healthcheck()

    # search
    def search_groups(self, regex: str) -> pd.DataFrame:
        return self._variableSearch.search_groups(regex).copy(deep=True)

    def search_variables(
        self,
        regex: str,
        *in_groups: GroupCode,
    ) -> pd.DataFrame:
        return self._variableSearch.search_variables(regex, *in_groups).copy(deep=True)

    # repo
    def get_geography_codes(
        self, for_domain: GeoDomain, *in_domains: GeoDomain
    ) -> pd.DataFrame:
        return self._geoRepo.get_geography_codes(for_domain, *in_domains).copy(
            deep=True
        )

    def get_groups(self) -> pd.DataFrame:
        return self._variableRepo.get_groups().copy(deep=True)

    def get_variables_by_group(self, *groups: GroupCode) -> pd.DataFrame:
        return self._variableRepo.get_variables_by_group(*groups).copy(deep=True)

    def get_all_variables(self) -> pd.DataFrame:
        return self._variableRepo.get_all_variables().copy(deep=True)

    def get_supported_geographies(self) -> pd.DataFrame:
        return self._geoRepo.get_supported_geographies().copy(deep=True)

    def get_stats(
        self,
        variables_to_query: List[VariableCode],
        for_domain: GeoDomain,
        *in_domains: GeoDomain,
    ) -> pd.DataFrame:
        return self._stats.get_stats(variables_to_query, for_domain, *in_domains).copy(
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
    def supported_geographies(self) -> SupportedGeoSet:
        return self._geoRepo.supported_geographies

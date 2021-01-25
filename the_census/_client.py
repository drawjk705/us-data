from typing import List

import pandas as pd

from the_census._api.fetch import ICensusApiFetchService
from the_census._geographies.interface import IGeographyRepository
from the_census._geographies.models import GeoDomain, GeoDomainTypes, SupportedGeoSet
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

    _variable_repo: IVariableRepository[pd.DataFrame]
    _variableSearch: IVariableSearchService[pd.DataFrame]
    _stats: ICensusStatisticsService[pd.DataFrame]
    _geo_repo: IGeographyRepository[pd.DataFrame]

    def __init__(
        self,
        variableRepo: IVariableRepository[pd.DataFrame],
        variableSearch: IVariableSearchService[pd.DataFrame],
        stats: ICensusStatisticsService[pd.DataFrame],
        api: ICensusApiFetchService,
        geoRepo: IGeographyRepository[pd.DataFrame],
    ) -> None:
        self._variable_repo = variableRepo
        self._variableSearch = variableSearch
        self._stats = stats
        self._geo_repo = geoRepo

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
        self, for_domain: GeoDomainTypes, *in_domains: GeoDomainTypes
    ) -> pd.DataFrame:
        return self._geo_repo.get_geography_codes(
            GeoDomain._from(for_domain),
            *[GeoDomain._from(in_domain) for in_domain in in_domains],
        ).copy(deep=True)

    def get_groups(self) -> pd.DataFrame:
        return self._variable_repo.get_groups().copy(deep=True)

    def get_variables_by_group(self, *groups: GroupCode) -> pd.DataFrame:
        return self._variable_repo.get_variables_by_group(*groups).copy(deep=True)

    def get_all_variables(self) -> pd.DataFrame:
        return self._variable_repo.get_all_variables().copy(deep=True)

    def get_supported_geographies(self) -> pd.DataFrame:
        return self._geo_repo.get_supported_geographies().copy(deep=True)

    def get_stats(
        self,
        variables_to_query: List[VariableCode],
        for_domain: GeoDomainTypes,
        *in_domains: GeoDomainTypes,
    ) -> pd.DataFrame:
        return self._stats.get_stats(
            variables_to_query,
            GeoDomain._from(for_domain),
            *[GeoDomain._from(in_domain) for in_domain in in_domains],
        ).copy(deep=True)

    # helpers

    # property variables for Jupyter notebook usage

    @property
    def variables(self) -> VariableSet:
        return self._variable_repo.variables

    @property
    def groups(self) -> GroupSet:
        return self._variable_repo.groups

    @property
    def supported_geographies(self) -> SupportedGeoSet:
        return self._geo_repo.supported_geographies

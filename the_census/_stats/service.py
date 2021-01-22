from functools import cache
from logging import Logger
from typing import Any, Dict, List, Set, Tuple

import pandas as pd

from the_census._api.interface import ICensusApiFetchService
from the_census._data_transformation.interface import ICensusDataTransformer
from the_census._exceptions import EmptyRepositoryException
from the_census._geographies.interface import IGeographyRepository
from the_census._geographies.models import GeoDomain
from the_census._stats.interface import ICensusStatisticsService
from the_census._utils.log.factory import ILoggerFactory
from the_census._utils.timer import timer
from the_census._utils.unique import get_unique
from the_census._variables.models import VariableCode
from the_census._variables.repository.interface import IVariableRepository


class CensusStatisticsService(ICensusStatisticsService[pd.DataFrame]):
    _api: ICensusApiFetchService
    _transformer: ICensusDataTransformer[pd.DataFrame]
    _variable_repo: IVariableRepository[pd.DataFrame]
    _geo_repo: IGeographyRepository[pd.DataFrame]
    _logger: Logger

    def __init__(
        self,
        api: ICensusApiFetchService,
        transformer: ICensusDataTransformer[pd.DataFrame],
        variableRepo: IVariableRepository[pd.DataFrame],
        geoRepo: IGeographyRepository[pd.DataFrame],
        loggerFactory: ILoggerFactory,
    ) -> None:
        self._api = api
        self._transformer = transformer
        self._variable_repo = variableRepo
        self._geo_repo = geoRepo
        self._logger = loggerFactory.getLogger(__name__)

    @timer
    def get_stats(
        self,
        variables_to_query: List[VariableCode],
        for_domain: GeoDomain,
        *in_domains: GeoDomain,
    ) -> pd.DataFrame:

        return self.__get_stats(
            variables_to_query=tuple(get_unique(variables_to_query)),
            for_domain=for_domain,
            in_domains=tuple(get_unique(in_domains)),
        )

    @cache
    def __get_stats(
        self,
        variables_to_query: Tuple[VariableCode],
        for_domain: GeoDomain,
        in_domains: Tuple[GeoDomain],
    ) -> pd.DataFrame:

        pullStats = lambda: self._api.stats(
            list(variables_to_query), for_domain, list(in_domains)
        )

        apiResults: List[List[List[str]]] = [res for res in pullStats()]

        (
            column_headers,
            type_conversions,
        ) = self._get_variable_names_and_type_conversions(set(variables_to_query))

        geo_domains_queried = [for_domain] + list(in_domains)

        supported_geos = self._geo_repo.get_supported_geographies()

        df = self._transformer.stats(
            apiResults,
            type_conversions,
            geo_domains_queried,
            column_headers,
            supported_geos,
        )

        return df

    def _get_variable_names_and_type_conversions(
        self, variables_to_query: Set[VariableCode]
    ) -> Tuple[Dict[VariableCode, str], Dict[str, Any]]:

        relevant_variables = {
            variable.code: variable
            for variable in self._variable_repo.variables.values()
            if variable.code in variables_to_query
        }
        if len(relevant_variables) != len(variables_to_query):
            msg = f"Queried {len(variables_to_query)} variables, but found only {len(relevant_variables)} in repository"

            self._logger.exception(msg)

            raise EmptyRepositoryException(msg)

        hasDuplicateNames = len(
            {v.cleaned_name for v in relevant_variables.values()}
        ) < len(variables_to_query)

        type_conversions: Dict[str, Any] = {}
        column_headers: Dict[VariableCode, str] = {}
        for k, v in relevant_variables.items():
            if v.predicate_type in ["int", "float"]:
                type_conversions.update({k: float})

            cleanedVarName = v.cleaned_name
            if hasDuplicateNames:
                cleanedVarName += f"_{v.group_code}"

            column_headers.update({k: cleanedVarName})

        return column_headers, type_conversions

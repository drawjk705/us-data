# pyright: reportUnknownMemberType=false

import os
from typing import List, cast

import dotenv
import pandas
import punq

from the_census._api.fetch import CensusApiFetchService
from the_census._api.interface import (
    ICensusApiFetchService,
    ICensusApiSerializationService,
)
from the_census._api.serialization import ApiSerializationService
from the_census._client import CensusClient
from the_census._config import CACHE_DIR, Config
from the_census._data_transformation.interface import ICensusDataTransformer
from the_census._data_transformation.service import CensusDataTransformer
from the_census._exceptions import NoCensusApiKeyException
from the_census._geographies.interface import IGeographyRepository
from the_census._geographies.models import GeoDomainTypes, SupportedGeoSet
from the_census._geographies.service import GeographyRepository
from the_census._helpers import list_available_datasets
from the_census._persistence.interface import ICache
from the_census._persistence.onDisk import OnDiskCache
from the_census._stats.interface import ICensusStatisticsService
from the_census._stats.service import CensusStatisticsService
from the_census._utils.log.configureLogger import DEFAULT_LOG_FILE, configureLogger
from the_census._utils.log.factory import ILoggerFactory, LoggerFactory
from the_census._variables.models import GroupCode, VariableCode
from the_census._variables.repository.interface import IVariableRepository
from the_census._variables.repository.models import GroupSet, VariableSet
from the_census._variables.repository.service import VariableRepository
from the_census._variables.search.interface import IVariableSearchService
from the_census._variables.search.service import VariableSearchService

# these are singletons
_serializer = ApiSerializationService()
_loggerFactory = LoggerFactory()


class Census:
    _client: CensusClient
    _config: Config

    def __init__(
        self,
        year: int,
        dataset: str = "acs",
        survey: str = "acs1",
        cache_dir: str = CACHE_DIR,
        should_load_from_existing_cache: bool = False,
        should_cache_on_disk: bool = False,
        replace_column_headers: bool = True,
        log_file: str = DEFAULT_LOG_FILE,
    ) -> None:
        dotenvPath = dotenv.find_dotenv()

        dotenv.load_dotenv(dotenvPath)

        api_key = os.getenv("CENSUS_API_KEY")

        if api_key is None:
            raise NoCensusApiKeyException("Could not find `CENSUS_API_KEY` in .env")

        self._config = Config(
            year,
            dataset,
            survey,
            cache_dir,
            should_load_from_existing_cache,
            should_cache_on_disk,
            replace_column_headers,
            api_key,
        )

        container = punq.Container()

        # singletons
        container.register(Config, instance=self._config)
        container.register(ICensusApiSerializationService, instance=_serializer)
        container.register(ILoggerFactory, instance=_loggerFactory)

        # services
        container.register(ICache[pandas.DataFrame], OnDiskCache)
        container.register(
            ICensusDataTransformer[pandas.DataFrame], CensusDataTransformer
        )
        container.register(ICensusApiFetchService, CensusApiFetchService)
        container.register(IVariableRepository[pandas.DataFrame], VariableRepository)
        container.register(
            IVariableSearchService[pandas.DataFrame], VariableSearchService
        )
        container.register(IGeographyRepository[pandas.DataFrame], GeographyRepository)
        container.register(
            ICensusStatisticsService[pandas.DataFrame], CensusStatisticsService
        )

        # the client
        container.register(CensusClient)

        configureLogger(log_file, datasetName=f"{dataset}.{survey}")

        # for Jupyter
        pandas.set_option("display.max_colwidth", None)  # type: ignore

        self._client = cast(CensusClient, container.resolve(CensusClient))

    # search
    def search_groups(self, regex: str) -> pandas.DataFrame:
        """
        Searches all group's based on their concept, according
        to `regex`. If the groups aren't yet in memory,
        this will handle that.

        Args:
            regex (str)

        Returns:
            pandas.DataFrame: with all of the relevant groups.
        """
        return self._client.search_groups(regex).copy(deep=True)

    def search_variables(
        self,
        regex: str,
        *in_groups: GroupCode,
    ) -> pandas.DataFrame:
        """
        - Searches variables based on `regex`.
        - It can search variables based on their name or group concept.
        - Specify `in_groups` with a list of group codes to restrict the search to
        variables within a particular group, or leave it empty to search all variables.
        - This will pull from the API whatever variables aren't in memory.

        Args:
            regex (str)
            in_groups (List[GroupCode], optional): if populated, this will search
            only the variables within the specified groups. Defaults to [].

        Returns:
            pandas.DataFrame: with all of the matched variables
        """
        return self._client.search_variables(regex, *in_groups).copy(deep=True)

    # repo
    def get_geography_codes(
        self, for_domain: GeoDomainTypes, *in_domains: GeoDomainTypes
    ) -> pandas.DataFrame:
        """
        Gets geography codes for the specified geography query.
        A GeoDomain is comprised of the domain (e.g., "state"), and an ID
        or wildcard. So passing in a `for_domain` of GeoDomain("congressional district", "*")
        would get all geography codes for all congressional district; providing an `inDomain`
        of, [GeoDomain("state", "06")] would constrain that search to the state with ID
        06 (California).

        Args:
            for_domain (GeoDomain): the primary geography region to query
            in_domains (List[GeoDomain], optional): any parents of the `for_domain`.
            Whether or not these must be populated and/or can have wildcards
            depends on the dataset/survey's supported geographies. (See `supported_geographies`
            below.). Defaults to [].

        Returns:
            pandas.DataFrame: [description]
        """
        return self._client.get_geography_codes(for_domain, *in_domains).copy(deep=True)

    def get_groups(self) -> pandas.DataFrame:
        """
        Gets all groups for the dataset/survey

        Returns:
            pandas.DataFrame: with all of the groups
        """
        return self._client.get_groups().copy(deep=True)

    def get_variables_by_group(self, *groups: GroupCode) -> pandas.DataFrame:
        """
        Gets all variables whose group is in `groups`.

        Args:
            groups (List[GroupCode]): codes of all the groups whose variables you want.

        Returns:
            pandas.DataFrame: with the queried variables.
        """
        return self._client.get_variables_by_group(*groups).copy(deep=True)

    def get_all_variables(self) -> pandas.DataFrame:
        """
        Gets all variables available to the dataset/survey.
        This may take a while.

        Returns:
            pandas.DataFrame: with all of the variables.
        """
        return self._client.get_all_variables().copy(deep=True)

    def get_supported_geographies(self) -> pandas.DataFrame:
        """
        Returns a DataFrame with all possible geography query
        patterns for the given dataset/survey.

        Returns:
            pandas.DataFrame
        """
        return self._client.get_supported_geographies().copy(deep=True)

    def get_stats(
        self,
        variables_to_query: List[VariableCode],
        for_domain: GeoDomainTypes,
        *in_domains: GeoDomainTypes,
    ) -> pandas.DataFrame:
        """
        Gets statistical data based on `variables_to_query`
        for the specified geographies.

        Args:
            variables_to_query (List[VariableCode]): the variables to query
            for_domain (GeoDomain)
            in_domains (List[GeoDomain], optional): Defaults to [].

        Returns:
            pandas.DataFrame: with the data
        """
        return self._client.get_stats(variables_to_query, for_domain, *in_domains).copy(
            deep=True
        )

    @staticmethod
    def list_available_datasets() -> pandas.DataFrame:
        """
        The name says it all

        Returns:
            pandas.DataFrame: DataFrame with all available datasets,
            along with their years & descriptions
        """
        return list_available_datasets()

    @staticmethod
    def help() -> None:
        print(
            "For more documentation on the census, see https://www2.census.gov/programs-surveys/"
        )
        print(
            "For more documentation on ACS subject defintiions, see https://www2.census.gov/programs-surveys/acs/tech_docs/subject_definitions/2019_ACSSubjectDefinitions.pdf"
        )

    #################################################
    # property variables for Jupyter notebook usage #
    #################################################

    @property
    def variables(self) -> VariableSet:
        return self._client.variables

    @property
    def groups(self) -> GroupSet:
        return self._client.groups

    @property
    def supported_geographies(self) -> SupportedGeoSet:
        return self._client.supported_geographies

    def __repr__(self) -> str:
        return f"<Census year={self._config.year} dataset={self._config.dataset} survey={self._config.survey}>"

    def __str__(self) -> str:
        return self.__repr__()

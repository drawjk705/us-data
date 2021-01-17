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
from the_census._dataTransformation.interface import ICensusDataTransformer
from the_census._dataTransformation.service import CensusDataTransformer
from the_census._exceptions import NoCensusApiKeyException
from the_census._geographies.interface import IGeographyRepository
from the_census._geographies.models import GeoDomain, SupportedGeoSet
from the_census._geographies.service import GeographyRepository
from the_census._helpers import listAvailableDataSets
from the_census._persistence.interface import ICache
from the_census._persistence.onDisk import OnDiskCache
from the_census._stats.interface import ICensusStatisticsService
from the_census._stats.service import CensusStatisticsService
from the_census._utils.log.configureLogger import DEFAULT_LOGFILE, configureLogger
from the_census._utils.log.factory import ILoggerFactory, LoggerFactory
from the_census._variables.models import GroupCode, VariableCode
from the_census._variables.repository.interface import IVariableRepository
from the_census._variables.repository.models import GroupSet, VariableSet
from the_census._variables.repository.service import VariableRepository
from the_census._variables.search.interface import IVariableSearchService
from the_census._variables.search.service import VariableSearchService

# these are singletons
_serializer = ApiSerializationService()
_transformer = CensusDataTransformer()
_loggerFactory = LoggerFactory()


class Census:
    _client: CensusClient
    _config: Config

    def __init__(
        self,
        year: int,
        datasetType: str = "acs",
        surveyType: str = "acs1",
        cacheDir: str = CACHE_DIR,
        shouldLoadFromExistingCache: bool = False,
        shouldCacheOnDisk: bool = False,
        replaceColumnHeaders: bool = True,
        logFile: str = DEFAULT_LOGFILE,
    ) -> None:
        dotenvPath = dotenv.find_dotenv()

        dotenv.load_dotenv(dotenvPath)

        apiKey = os.getenv("CENSUS_API_KEY")

        if apiKey is None:
            raise NoCensusApiKeyException("Could not find `CENSUS_API_KEY` in .env")

        self._config = Config(
            year,
            datasetType,
            surveyType,
            cacheDir,
            shouldLoadFromExistingCache,
            shouldCacheOnDisk,
            replaceColumnHeaders,
            apiKey,
        )

        container = punq.Container()

        # singletons
        container.register(Config, instance=self._config)
        container.register(ICensusApiSerializationService, instance=_serializer)
        container.register(
            ICensusDataTransformer[pandas.DataFrame], instance=_transformer
        )
        container.register(ILoggerFactory, instance=_loggerFactory)

        # services
        container.register(ICache[pandas.DataFrame], OnDiskCache)
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

        configureLogger(logFile)

        # for Jupyter
        pandas.set_option("display.max_colwidth", None)  # type: ignore

        self._client = cast(CensusClient, container.resolve(CensusClient))

    # search
    def searchGroups(self, regex: str) -> pandas.DataFrame:
        """
        Searches all group's based on their concept, according
        to `regex`

        Args:
            regex (str)

        Returns:
            pandas.DataFrame: with all of the relevant groups.
        """
        return self._client.searchGroups(regex).copy(deep=True)

    def searchVariables(
        self,
        regex: str,
        *inGroups: GroupCode,
    ) -> pandas.DataFrame:
        """
        - Searches variables based on `regex`.
        - It can search variables based on their name or group concept.
        - Specify `inGroups` with a list of group codes to restrict the search to
        variables within a particular group, or leave it empty to search all variables.
        - This will pull from the API whatever variables aren't in memory.

        Args:
            regex (str)
            inGroups (List[GroupCode], optional): if populated, this will search
            only the variables within the specified groups. Defaults to [].

        Returns:
            pandas.DataFrame: with all of the matched variables
        """
        return self._client.searchVariables(regex, *inGroups).copy(deep=True)

    # repo
    def getGeographyCodes(
        self, forDomain: GeoDomain, *inDomains: GeoDomain
    ) -> pandas.DataFrame:
        """
        Gets geography codes for the specified geography query.
        A GeoDomain is comprised of the domain (e.g., "state"), and an ID
        or wildcard. So passing in a `forDomain` of GeoDomain("congressional district", "*")
        would get all geography codes for all congressional district; providing an `inDomain`
        of, [GeoDomain("state", "06")] would constrain that search to the state with ID
        06 (California).

        Args:
            forDomain (GeoDomain): the primary geography region to query
            inDomains (List[GeoDomain], optional): any parents of the `forDomain`.
            Whether or not these must be populated and/or can have wildcards
            depends on the dataset/survey's supported geographies. (See `supportedGeographies`
            below.). Defaults to [].

        Returns:
            pandas.DataFrame: [description]
        """
        return self._client.getGeographyCodes(forDomain, *inDomains).copy(deep=True)

    def getGroups(self) -> pandas.DataFrame:
        """
        Gets all groups for the dataset/survey

        Returns:
            pandas.DataFrame: with all of the groups
        """
        return self._client.getGroups().copy(deep=True)

    def getVariablesByGroup(self, *groups: GroupCode) -> pandas.DataFrame:
        """
        Gets all variables whose group is in `groups`.

        Args:
            groups (List[GroupCode]): codes of all the groups whose variables you want.

        Returns:
            pandas.DataFrame: with the queried variables.
        """
        return self._client.getVariablesByGroup(*groups).copy(deep=True)

    def getAllVariables(self) -> pandas.DataFrame:
        """
        Gets all variables available to the dataset/survey.
        This may take a while.

        Returns:
            pandas.DataFrame: with all of the variables.
        """
        return self._client.getAllVariables().copy(deep=True)

    def getSupportedGeographies(self) -> pandas.DataFrame:
        """
        Returns a DataFrame with all possible geography query
        patterns for the given dataset/survey.

        Returns:
            pandas.DataFrame
        """
        return self._client.getSupportedGeographies().copy(deep=True)

    def getStats(
        self,
        variablesToQuery: List[VariableCode],
        forDomain: GeoDomain,
        *inDomains: GeoDomain,
    ) -> pandas.DataFrame:
        """
        Gets statistical data based on `variablesToQuery`
        for the specified geographies.

        Args:
            variablesToQuery (List[VariableCode]): the variables to query
            forDomain (GeoDomain)
            inDomains (List[GeoDomain], optional): Defaults to [].

        Returns:
            pandas.DataFrame: with the data
        """
        return self._client.getStats(variablesToQuery, forDomain, *inDomains).copy(
            deep=True
        )

    @staticmethod
    def listAvailabeDatasets() -> pandas.DataFrame:
        """
        The name says it all

        Returns:
            pandas.DataFrame: DataFrame with all available datasets,
            along with their years & descriptions
        """
        return listAvailableDataSets()

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
    def supportedGeographies(self) -> SupportedGeoSet:
        return self._client.supportedGeographies

    def __repr__(self) -> str:
        return f"<Census year={self._config.year} dataset={self._config.datasetType} survey={self._config.surveyType}>"

    def __str__(self) -> str:
        return self.__repr__()

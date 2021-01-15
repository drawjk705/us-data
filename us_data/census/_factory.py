# pyright: reportUnknownMemberType=false

import os
from typing import cast

import dotenv
import pandas
import punq

from us_data.census._api.fetch import CensusApiFetchService
from us_data.census._api.interface import (
    ICensusApiFetchService,
    ICensusApiSerializationService,
)
from us_data.census._api.serialization import ApiSerializationService
from us_data.census._client.census import Census
from us_data.census._config import CACHE_DIR, Config
from us_data.census._dataTransformation.interface import ICensusDataTransformer
from us_data.census._dataTransformation.service import CensusDataTransformer
from us_data.census._exceptions import NoCensusApiKeyException
from us_data.census._geographies.interface import IGeographyRepository
from us_data.census._geographies.service import GeographyRepository
from us_data.census._persistence.interface import ICache
from us_data.census._persistence.onDisk import OnDiskCache
from us_data.census._stats.interface import ICensusStatisticsService
from us_data.census._stats.service import CensusStatisticsService
from us_data.census._variables.repository.interface import IVariableRepository
from us_data.census._variables.repository.service import VariableRepository
from us_data.census._variables.search.interface import IVariableSearchService
from us_data.census._variables.search.service import VariableSearchService
from us_data._utils.log.configureLogger import DEFAULT_LOGFILE, configureLogger
from us_data._utils.log.factory import ILoggerFactory, LoggerFactory

# these are singletons
serializer = ApiSerializationService()
transformer = CensusDataTransformer()
loggerFactory = LoggerFactory()


def getCensus(
    year: int,
    datasetType: str = "acs",
    surveyType: str = "acs1",
    cacheDir: str = CACHE_DIR,
    shouldLoadFromExistingCache: bool = False,
    shouldCacheOnDisk: bool = False,
    replaceColumnHeaders: bool = True,
    logFile: str = DEFAULT_LOGFILE,
) -> Census:
    """
    Dependency-injects all services to return the census client.
    This should be called once per set of census-data being queried.
    So if you want to start querying for the 2019 ACS1 just do this:

    >>> c = getCensus(2019, "acs", "acs1")

    and use `c` to make all subsequent queries.

    If you decide you're interested in the 2019 ACS5, do this:

    >>> d = getCensus(2019, "acs", "acs5")

    and perform all subsequent operations with `d`.



    Args:
        year (int): year of the survey
        datasetType (DatasetType, optional). Defaults to DatasetType.ACS.
        surveyType (SurveyType, optional). Defaults to SurveyType.ACS1.
        cacheDir (str, optional): where to cache data. Defaults to CACHE_DIR.
        shouldLoadFromExistingCache (bool, optional): whether or not to check the on-disk
        cache before making API requests. If `False`, this will purge any existing
        caches on disk. Defaults to False.
        shouldCacheOnDisk (bool, optional): whether or not to cache data on-dks. Defaults to False.
        replaceColumnHeaders (bool, optional): whether or not to replace column headers
        of census stats with variable names (as opposed to codes). Defaults to True.
        logFile (str, optional): where to write logs. Defaults to DEFAULT_LOGFILE.

    Returns:
        Census
    """

    dotenvPath = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenvPath)

    apiKey = os.getenv("CENSUS_API_KEY")

    if apiKey is None:
        raise NoCensusApiKeyException("Could not find `CENSUS_API_KEY` in .env")

    config = Config(
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
    container.register(Config, instance=config)
    container.register(ICensusApiSerializationService, instance=serializer)
    container.register(ICensusDataTransformer[pandas.DataFrame], instance=transformer)
    container.register(ILoggerFactory, instance=loggerFactory)

    # services
    container.register(ICache[pandas.DataFrame], OnDiskCache)
    container.register(ICensusApiFetchService, CensusApiFetchService)
    container.register(IVariableRepository[pandas.DataFrame], VariableRepository)
    container.register(IVariableSearchService[pandas.DataFrame], VariableSearchService)
    container.register(IGeographyRepository[pandas.DataFrame], GeographyRepository)
    container.register(
        ICensusStatisticsService[pandas.DataFrame], CensusStatisticsService
    )

    # the client
    container.register(Census)

    configureLogger(logFile)

    # for Jupyter
    pandas.set_option("display.max_colwidth", None)  # type: ignore

    return cast(Census, container.resolve(Census))

# pyright: reportUnknownMemberType=false

import os
from typing import cast

import dotenv
import pandas
import punq

from census.api.fetch import CensusApiFetchService
from census.api.interface import (ICensusApiFetchService,
                                  ICensusApiSerializationService)
from census.api.serialization import ApiSerializationService
from census.client.census import Census
from census.config import CACHE_DIR, Config
from census.dataTransformation.interface import ICensusDataTransformer
from census.dataTransformation.service import CensusDataTransformer
from census.exceptions import NoCensusApiKeyException
from census.geographies.interface import IGeographyRepository
from census.geographies.service import GeographyRepository
from census.log.configureLogger import DEFAULT_LOGFILE, configureLogger
from census.log.factory import ILoggerFactory, LoggerFactory
from census.persistence.interface import ICache
from census.persistence.onDisk import OnDiskCache
from census.stats.interface import ICensusStatisticsService
from census.stats.service import CensusStatisticsService
from census.variables.repository.interface import IVariableRepository
from census.variables.repository.service import VariableRepository
from census.variables.search.interface import IVariableSearchService
from census.variables.search.service import VariableSearchService

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

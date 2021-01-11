# pyright: reportUnknownMemberType=false

from census.geographies.service import GeographyRepository
from census.geographies.interface import IGeographyRepository
from census.logging.configureLogger import DEFAULT_LOGFILE, configureLogger
from typing import cast

import pandas
from census.persistence.interface import ICache
from census.persistence.onDisk import OnDiskCache
from census.stats.service import CensusStatisticsService
from census.stats.interface import ICensusStatisticsService
from census.variables.search.interface import IVariableSearchService
from census.variables.repository.interface import IVariableRepository
from census.variables.repository.service import VariableRepository
from census.dataTransformation.interface import IDataTransformer
from census.variables.search.service import VariableSearchService
from census.api.interface import IApiFetchService, IApiSerializationService
import punq

from census.api.fetch import ApiFetchService
from census.api.serialization import ApiSerializationService
from census.config import CACHE_DIR, Config
from census.dataTransformation.service import DataFrameTransformer
from census.client.census import Census

# these are singletons
serializer = ApiSerializationService()
transformer = DataFrameTransformer()


def getCensus(
    year: int,
    datasetType: str = "acs",
    surveyType: str = "acs1",
    cacheDir: str = CACHE_DIR,
    shouldLoadFromExistingCache: bool = False,
    shouldCacheOnDisk: bool = False,
    shouldReplaceColumnHeaders: bool = True,
    logFile: str = DEFAULT_LOGFILE,
) -> Census:
    """
    Dependency-injects all services to return the census client.
    This should be called once per set of census-data being queried.
    So if you want to start querying for the 2019 ACS1 just do this:

    >>> c = getCensus(2019, DatasetType.ACS, SurveyType.ACS1)

    and use `c` to make all subsequent queries.

    If you decide you're interested in the 2019 ACS5, do this:

    >>> d = getCensus(2019, DatasetType.ACS, SurveyType.ACS5)

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
        logFile (str, optional): where to write logs. Defaults to DEFAULT_LOGFILE.

    Returns:
        Census
    """

    config = Config(
        year,
        datasetType,
        surveyType,
        cacheDir,
        shouldLoadFromExistingCache,
        shouldCacheOnDisk,
        replaceColumnHeaders=shouldReplaceColumnHeaders,
    )

    container = punq.Container()

    # singletons
    container.register(Config, instance=config)
    container.register(IApiSerializationService, instance=serializer)
    container.register(IDataTransformer[pandas.DataFrame], instance=transformer)

    # services
    container.register(ICache[pandas.DataFrame], OnDiskCache)
    container.register(IApiFetchService, ApiFetchService)
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

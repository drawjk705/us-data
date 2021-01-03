# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false

from census.utils.configureLogger import DEFAULT_LOGFILE, configureLogger
from typing import cast

import pandas
from census.variables.persistence.interface import ICache
from census.variables.persistence.onDisk import OnDiskCache
from census.stats.statsAsDataFrame import CensusStatisticsService
from census.stats.interface import ICensusStatisticsService
from census.variables.search.interface import IVariableSearchService
from census.variables.repository.interface import IVariableRepository
from census.variables.repository.storeInDataFrame import VariableRepository
from census.dataTransformation.interface import IDataTransformer
from census.variables.search.searchDataFrame import VariableSearchService
from census.api.interface import IApiFetchService, IApiSerializationService
import punq

from census.api.fetch import ApiFetchService
from census.api.serialization import ApiSerializationService
from census.config import CACHE_DIR, Config
from census.dataTransformation.transformToDataFrame import DataFrameTransformer
from census.client.census import Census
from census.models import DatasetType, SurveyType

serializer = ApiSerializationService()
transformer = DataFrameTransformer()


def getCensus(
    year: int,
    datasetType: DatasetType = DatasetType.ACS,
    surveyType: SurveyType = SurveyType.ACS1,
    cacheDir: str = CACHE_DIR,
    shouldLoadFromExistingCache: bool = False,
    shouldCacheOnDisk: bool = False,
    logFile: str = DEFAULT_LOGFILE,
) -> Census:
    config = Config(
        year,
        datasetType,
        surveyType,
        cacheDir,
        shouldLoadFromExistingCache,
        shouldCacheOnDisk,
    )

    container = punq.Container()

    # singletons
    container.register(Config, instance=config)
    container.register(IApiSerializationService, instance=serializer)
    container.register(IDataTransformer[pandas.DataFrame], instance=transformer)

    container.register(ICache[pandas.DataFrame], OnDiskCache)
    container.register(IApiFetchService, ApiFetchService)
    container.register(IVariableRepository[pandas.DataFrame], VariableRepository)
    container.register(IVariableSearchService[pandas.DataFrame], VariableSearchService)
    container.register(
        ICensusStatisticsService[pandas.DataFrame], CensusStatisticsService
    )

    container.register(Census)

    configureLogger(logFile)

    pandas.set_option("display.max_colwidth", -1)

    return cast(Census, container.resolve(Census))

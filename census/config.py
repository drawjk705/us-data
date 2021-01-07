from dataclasses import dataclass
from census.models import SurveyType, DatasetType


CACHE_DIR = "cache"


@dataclass(frozen=True)
class Config:
    """
    Stores basic information for hitting the API,
    so that we don't need to pass the same variables
    around all of the time:
    - Survey year
    - Dataset type
    - Survey type
    - Where to cache data
    - Whether or not to check the on-disk cache for data before hitting the API
    - Whether or not to cache variable/group/geography data on-disk
    """

    year: int = 2020
    datasetType: DatasetType = DatasetType.ACS
    surveyType: SurveyType = SurveyType.ACS1
    cacheDir: str = CACHE_DIR
    shouldLoadFromExistingCache: bool = False
    shouldCacheOnDisk: bool = False
    replaceColumnHeaders: bool = False

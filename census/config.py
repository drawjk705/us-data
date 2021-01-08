from dataclasses import dataclass


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
    datasetType: str = "acs"
    surveyType: str = "acs1"
    cacheDir: str = CACHE_DIR
    shouldLoadFromExistingCache: bool = False
    shouldCacheOnDisk: bool = False
    replaceColumnHeaders: bool = False

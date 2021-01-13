from dataclasses import dataclass

CACHE_DIR = "cache"


@dataclass(frozen=True)
class Config:
    """
    Stores basic information so that we don't need to
    pass the same variables around all of the time
    """

    year: int = 2020
    datasetType: str = "acs"
    surveyType: str = "acs1"
    cacheDir: str = CACHE_DIR
    shouldLoadFromExistingCache: bool = False
    shouldCacheOnDisk: bool = False
    replaceColumnHeaders: bool = False
    apiKey: str = ""

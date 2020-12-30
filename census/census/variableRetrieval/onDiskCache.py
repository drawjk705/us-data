import logging
import shutil
from pathlib import Path
from typing import Optional

import pandas as pd
from census.models import DatasetType, SurveyType

CACHE_DIR = "cache"

LOG_PREFIX = "[On-Disk Cache]"


class OnDiskCache:
    __shouldLoadFromExistingCache: bool

    __onDiskCacheDir: str

    def __init__(
        self,
        year: int,
        datasetType: DatasetType = DatasetType.ACS,
        surveyType: SurveyType = SurveyType.ACS1,
        shouldLoadFromExistingCache: bool = False,
    ) -> None:

        logging.info(
            f"{LOG_PREFIX} creating cache for {year}/{datasetType.value}/{surveyType.value}"
        )

        self.__shouldLoadFromExistingCache = shouldLoadFromExistingCache

        self.__onDiskCacheDir = (
            f"{CACHE_DIR}/{year}/{datasetType.value}/{surveyType.value}"
        )

        self.__setUpOnDiskCache()

    def __setUpOnDiskCache(self) -> None:
        logging.info(f"{LOG_PREFIX} setting up on disk cache")

        if not self.__shouldLoadFromExistingCache:
            logging.info(f"{LOG_PREFIX} purging on disk cache")

            if Path(CACHE_DIR).exists():
                shutil.rmtree(CACHE_DIR)

        path = Path(self.__onDiskCacheDir)
        path.mkdir(parents=True, exist_ok=True)

    def persist(
        self, file: Path, data: pd.DataFrame, parentPath: Optional[Path] = None
    ) -> None:
        path: Path

        if parentPath:
            path = Path(f"{self.__onDiskCacheDir}/{parentPath}")
            path.mkdir(parents=True, exist_ok=True)
            path /= file
        else:
            path = Path(f"{self.__onDiskCacheDir}/{file}")

        logging.info(f"{LOG_PREFIX} persisting {path} on disk")

        data.to_csv(str(path.absolute()))

    def getFromCache(
        self, file: Path, parentPath: Optional[Path] = None
    ) -> pd.DataFrame:
        path: Path

        if parentPath:
            path = Path(f"{self.__onDiskCacheDir}/{parentPath}")
            path.mkdir(parents=True, exist_ok=True)
            path /= file
        else:
            path = Path(f"{self.__onDiskCacheDir}/{file}")

        if not path.exists():
            logging.info(f"{LOG_PREFIX} cache miss for {file}")
            return pd.DataFrame()

        logging.info(f"{LOG_PREFIX} cache hit for {file}")

        return pd.read_csv(path.absolute())  # type: ignore
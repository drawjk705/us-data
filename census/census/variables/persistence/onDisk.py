import logging
import shutil
from pathlib import Path

import pandas as pd
from census.config import Config
from census.variables.persistence.interface import ICache

LOG_PREFIX = "[On-Disk Cache]"


class OnDiskCache(ICache[pd.DataFrame]):
    __shouldLoadFromExistingCache: bool
    __cachePath: Path
    _config: Config

    def __init__(
        self,
        config: Config,
    ) -> None:
        self._config = config
        self.__cachePath = Path(
            f"{config.cacheDir}/{config.year}/{config.datasetType.value}/{config.surveyType.value}"
        )

        logging.info(f"{LOG_PREFIX} creating cache for {self.__cachePath}")

        self.__shouldLoadFromExistingCache = config.shouldLoadFromExistingCache

        self.__setUpOnDiskCache()

    def __setUpOnDiskCache(self) -> None:
        self.__log("setting up on disk cache")

        if not self.__shouldLoadFromExistingCache:
            self.__log("purging on disk cache")

            if Path(self._config.cacheDir).exists():
                shutil.rmtree(self._config.cacheDir)

        self.__cachePath.mkdir(parents=True, exist_ok=True)

    def put(self, resource: str, data: pd.DataFrame) -> None:
        path = self.__cachePath / Path(resource)

        path.parent.mkdir(parents=True, exist_ok=True)

        self.__log(f"persisting {path} on disk")

        data.to_csv(str(path.absolute()))

    def get(self, resource: str) -> pd.DataFrame:
        path = self.__cachePath / Path(resource)

        if not path.exists():
            logging.info(f"{LOG_PREFIX} cache miss for {path}")
            return pd.DataFrame()

        self.__log(f"cache hit for {path}")

        return pd.read_csv(path.absolute())  # type: ignore

    def __log(self, msg: str) -> None:
        logging.info(f"{LOG_PREFIX} {msg}")

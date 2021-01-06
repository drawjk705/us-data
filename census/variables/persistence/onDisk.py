from census.utils.timer import timer
import logging
import shutil
from pathlib import Path

import pandas as pd
from census.config import Config
from census.variables.persistence.interface import ICache

LOG_PREFIX = "[On-Disk Cache]"


class OnDiskCache(ICache[pd.DataFrame]):
    __cachePath: Path
    _config: Config

    def __init__(
        self,
        config: Config,
    ) -> None:
        self._config = config

        if not self._config.shouldCacheOnDisk:
            self.__log("Not creating an on-disk cache")
            return

        self.__cachePath = Path(
            f"{config.cacheDir}/{config.year}/{config.datasetType.value}/{config.surveyType.value}"
        )

        self.__log(f"creating cache for {self.__cachePath}")

        self.__setUpOnDiskCache()

    @timer
    def __setUpOnDiskCache(self) -> None:
        self.__log("setting up on disk cache")

        if not self._config.shouldLoadFromExistingCache:
            self.__log("purging on disk cache")

            if Path(self._config.cacheDir).exists():
                shutil.rmtree(self._config.cacheDir)

        self.__cachePath.mkdir(parents=True, exist_ok=True)

    @timer
    def put(self, resource: str, data: pd.DataFrame) -> bool:
        if not self._config.shouldCacheOnDisk:
            return False

        path = self.__cachePath.joinpath(Path(resource))

        if path.exists():
            self.__log(f'resource "{resource}" already exists; terminating')
            return False

        path.parent.mkdir(parents=True, exist_ok=True)

        self.__log(f'persisting "{path}" on disk')

        data.to_csv(str(path.absolute()), index=False)
        return True

    @timer
    def get(self, resource: str) -> pd.DataFrame:
        if (
            not self._config.shouldLoadFromExistingCache
            or not self._config.shouldCacheOnDisk
        ):
            return pd.DataFrame()

        path = self.__cachePath.joinpath(Path(resource))

        if not path.exists():
            self.__log(f'cache miss for "{path}"')
            return pd.DataFrame()

        self.__log(f'cache hit for "{path}"')

        return pd.read_csv(path.absolute())  # type: ignore

    def __log(self, msg: str) -> None:
        logging.debug(f"{LOG_PREFIX} {msg}")

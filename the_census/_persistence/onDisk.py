import shutil
from logging import Logger
from pathlib import Path

import pandas as pd

from the_census._config import Config
from the_census._persistence.interface import ICache
from the_census._utils.log.factory import ILoggerFactory
from the_census._utils.timer import timer

LOG_PREFIX = "[On-Disk Cache]"


class OnDiskCache(ICache[pd.DataFrame]):
    _config: Config
    _logger: Logger

    def __init__(self, config: Config, loggerFactory: ILoggerFactory) -> None:
        self._config = config
        self._logger = loggerFactory.getLogger(__name__)

        self._cachePath = Path(
            f"{config.cacheDir}/{config.year}/{config.datasetType}/{config.surveyType}"
        )

        if not self._config.shouldCacheOnDisk:
            self._logger.debug("Not creating an on-disk cache")
            return

        self._logger.debug(f"creating cache for {self._cachePath}")

        self.__setUpOnDiskCache()

    @timer
    def __setUpOnDiskCache(self) -> None:
        self._logger.debug("setting up on disk cache")

        if not self._config.shouldLoadFromExistingCache:
            self._logger.debug("purging on disk cache")

            if Path(self._config.cacheDir).exists():
                shutil.rmtree(self._config.cacheDir)

        self._cachePath.mkdir(parents=True, exist_ok=True)

    @timer
    def put(self, resource: str, data: pd.DataFrame) -> bool:
        if not self._config.shouldCacheOnDisk:
            return True

        path = self._cachePath.joinpath(Path(resource))

        if path.exists():
            self._logger.debug(f'resource "{resource}" already exists; terminating')
            return False

        path.parent.mkdir(parents=True, exist_ok=True)

        self._logger.debug(f'persisting "{path}" on disk')

        data.to_csv(str(path.absolute()), index=False)
        return True

    @timer
    def get(self, resource: str) -> pd.DataFrame:
        if (
            not self._config.shouldLoadFromExistingCache
            or not self._config.shouldCacheOnDisk
        ):
            return pd.DataFrame()

        path = self._cachePath.joinpath(Path(resource))

        if not path.exists():
            self._logger.debug(f'cache miss for "{path}"')
            return pd.DataFrame()

        self._logger.debug(f'cache hit for "{path}"')

        return pd.read_csv(path.absolute())  # type: ignore

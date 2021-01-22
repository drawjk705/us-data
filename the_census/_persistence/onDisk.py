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

    def __init__(self, config: Config, logger_factory: ILoggerFactory) -> None:
        self._config = config
        self._logger = logger_factory.getLogger(__name__)

        self._cache_path = Path(
            f"{config.cache_dir}/{config.year}/{config.dataset}/{config.survey}"
        )

        if not self._config.should_cache_on_disk:
            self._logger.debug("Not creating an on-disk cache")
            return

        self._logger.debug(f"creating cache for {self._cache_path}")

        self.__set_up_on_disk_cache()

    @timer
    def __set_up_on_disk_cache(self) -> None:
        self._logger.debug("setting up on disk cache")

        if not self._config.should_load_from_existing_cache:
            self._logger.debug("purging on disk cache")

            if Path(self._config.cache_dir).exists():
                shutil.rmtree(self._config.cache_dir)

        self._cache_path.mkdir(parents=True, exist_ok=True)

    @timer
    def put(self, resource: str, data: pd.DataFrame) -> bool:
        if not self._config.should_cache_on_disk:
            return True

        path = self._cache_path.joinpath(Path(resource))

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
            not self._config.should_load_from_existing_cache
            or not self._config.should_cache_on_disk
        ):
            return pd.DataFrame()

        path = self._cache_path.joinpath(Path(resource))

        if not path.exists():
            self._logger.debug(f'cache miss for "{path}"')
            return pd.DataFrame()

        self._logger.debug(f'cache hit for "{path}"')

        return pd.read_csv(path.absolute())  # type: ignore

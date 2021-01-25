from functools import cache
from logging import Logger
from typing import List, Tuple, cast

import pandas as pd

from the_census._api.interface import ICensusApiFetchService
from the_census._data_transformation.interface import ICensusDataTransformer
from the_census._geographies.interface import IGeographyRepository
from the_census._geographies.models import GeoDomain, SupportedGeoSet
from the_census._persistence.interface import ICache
from the_census._utils.log.factory import ILoggerFactory
from the_census._utils.timer import timer
from the_census._utils.unique import get_unique

SUPPORTED_GEOS_FILE = "supported_geographies.csv"


class GeographyRepository(IGeographyRepository[pd.DataFrame]):
    _cache: ICache[pd.DataFrame]
    _api: ICensusApiFetchService
    _transformer: ICensusDataTransformer[pd.DataFrame]
    _logger: Logger

    def __init__(
        self,
        cache: ICache[pd.DataFrame],
        api: ICensusApiFetchService,
        transformer: ICensusDataTransformer[pd.DataFrame],
        logger_factory: ILoggerFactory,
    ) -> None:
        self._cache = cache
        self._api = api
        self._transformer = transformer
        self._logger = logger_factory.getLogger(__name__)

        self._supported_geographies = SupportedGeoSet()

        self.__populate_repository()

    @timer
    def get_geography_codes(
        self, for_domain: GeoDomain, *in_domains: GeoDomain
    ) -> pd.DataFrame:
        return self.__get_geography_codes(
            for_domain, in_domains=tuple(get_unique(in_domains))
        )

    @cache
    def __get_geography_codes(
        self, for_domain: GeoDomain, in_domains: Tuple[GeoDomain, ...] = ()
    ) -> pd.DataFrame:
        self._logger.debug(f"getting geography codes for {for_domain} in {in_domains}")
        res = self._api.geography_codes(for_domain, list(in_domains))

        if len(res) == 0:
            return pd.DataFrame()

        df = self._transformer.geography_codes(res)

        return df

    @timer
    def get_supported_geographies(self) -> pd.DataFrame:
        return self.__get_supported_geographies()

    @cache
    def __get_supported_geographies(self) -> pd.DataFrame:
        self._logger.debug("getting supported geographies")

        df = self._cache.get(SUPPORTED_GEOS_FILE)

        if df is None:
            df = pd.DataFrame()

        if df.empty:
            res = self._api.supported_geographies()

            if len(res) == 0:
                return pd.DataFrame()

            df = self._transformer.supported_geographies(res)

            self._cache.put(SUPPORTED_GEOS_FILE, df)

        self._supported_geographies.add(*df["name"].tolist())

        return df

    def __populate_repository(self) -> None:
        self._logger.debug("Trying to populate geography repository")

        df = self._cache.get(SUPPORTED_GEOS_FILE)

        if df is None or df.empty:
            self._logger.debug("Could not populate geography repository")
            return

        self._supported_geographies.add(*set(cast(List[str], df["name"].tolist())))

        self._logger.debug("Populated geography repository")

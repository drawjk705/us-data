from functools import cache
from typing import Tuple

import pandas as pd

from us_data.census.api.interface import ICensusApiFetchService
from us_data.census.dataTransformation.interface import ICensusDataTransformer
from us_data.census.geographies.interface import IGeographyRepository
from us_data.census.geographies.models import GeoDomain, SupportedGeoSet
from us_data.census.persistence.interface import ICache
from us_data.utils.timer import timer
from us_data.utils.unique import getUnique

SUPPORTED_GEOS_FILE = "supportedGeographies.csv"


class GeographyRepository(IGeographyRepository[pd.DataFrame]):
    _cache: ICache[pd.DataFrame]
    _api: ICensusApiFetchService
    _transformer: ICensusDataTransformer[pd.DataFrame]

    def __init__(
        self,
        cache: ICache[pd.DataFrame],
        api: ICensusApiFetchService,
        transformer: ICensusDataTransformer[pd.DataFrame],
    ) -> None:
        self._cache = cache
        self._api = api
        self._transformer = transformer

        self._supportedGeographies = SupportedGeoSet()

    @timer
    def getGeographyCodes(
        self, forDomain: GeoDomain, *inDomains: GeoDomain
    ) -> pd.DataFrame:
        return self.__getGeographyCodes(
            forDomain, inDomains=tuple(getUnique(inDomains))
        )

    @cache
    def __getGeographyCodes(
        self, forDomain: GeoDomain, inDomains: Tuple[GeoDomain, ...] = ()
    ) -> pd.DataFrame:
        res = self._api.geographyCodes(forDomain, list(inDomains))
        df = self._transformer.geographyCodes(res)

        return df

    @timer
    def getSupportedGeographies(self) -> pd.DataFrame:
        return self.__getSupportedGeographies()

    @cache
    def __getSupportedGeographies(self) -> pd.DataFrame:
        df = self._cache.get(SUPPORTED_GEOS_FILE)

        if df is None:
            df = pd.DataFrame()

        if df.empty:
            res = self._api.supportedGeographies()
            df = self._transformer.supportedGeographies(res)

            self._cache.put(SUPPORTED_GEOS_FILE, df)

        self._supportedGeographies.add(*df["name"].tolist())

        return df

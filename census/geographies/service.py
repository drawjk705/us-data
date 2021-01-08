from census.geographies.models import SupportedGeoSet
from census.utils.unique import getUnique
from functools import cache
from typing import Tuple
from census.utils.timer import timer
from census.geographies.models import GeoDomain
from census.geographies.interface import IGeographyRepository

import pandas as pd
from census.api.interface import IApiFetchService
from census.persistence.interface import ICache
from census.dataTransformation.interface import IDataTransformer

SUPPORTED_GEOS_FILE = "supportedGeographies.csv"


class GeographyRepository(IGeographyRepository[pd.DataFrame]):
    _cache: ICache[pd.DataFrame]
    _api: IApiFetchService
    _transformer: IDataTransformer[pd.DataFrame]

    def __init__(
        self,
        cache: ICache[pd.DataFrame],
        api: IApiFetchService,
        transformer: IDataTransformer[pd.DataFrame],
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
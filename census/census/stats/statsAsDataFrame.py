from typing import List

import pandas as pd
from census.api.interface import IApiFetchService
from census.api.models import GroupVariable
from census.dataTransformation.interface import IDataTransformer
from census.models import GeoDomain
from census.stats.interface import ICensusStatisticsService


class CensusStatisticToDataFrameService(ICensusStatisticsService[pd.DataFrame]):
    _api: IApiFetchService
    _transformer: IDataTransformer[pd.DataFrame]

    def __init__(
        self, api: IApiFetchService, transformer: IDataTransformer[pd.DataFrame]
    ) -> None:
        self._api = api
        self._transformer = transformer

    def getStats(
        self,
        variablesToQuery: List[GroupVariable],
        forDomain: GeoDomain,
        inDomains: List[GeoDomain],
    ) -> pd.DataFrame:
        variableCodes = [v.code for v in variablesToQuery]

        apiRes = self._api.stats(variableCodes, forDomain, inDomains)
        df = self._transformer.stats(apiRes, variablesToQuery)

        return df

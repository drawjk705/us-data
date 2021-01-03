from census.variables.repository.interface import IVariableRepository
from census.variables.models import VariableCode
from census.utils.unique import getUnique
from functools import cache
from typing import List, Tuple

import pandas as pd
from census.api.interface import IApiFetchService
from census.dataTransformation.interface import IDataTransformer
from census.models import GeoDomain
from census.stats.interface import ICensusStatisticsService


class CensusStatisticsService(ICensusStatisticsService[pd.DataFrame]):
    _api: IApiFetchService
    _transformer: IDataTransformer[pd.DataFrame]
    _variableRepo: IVariableRepository[pd.DataFrame]

    def __init__(
        self,
        api: IApiFetchService,
        transformer: IDataTransformer[pd.DataFrame],
        variableRepo: IVariableRepository[pd.DataFrame],
    ) -> None:
        self._api = api
        self._transformer = transformer
        self._variableRepo = variableRepo

    def getStats(
        self,
        variablesToQuery: List[VariableCode],
        forDomain: GeoDomain,
        inDomains: List[GeoDomain] = [],
    ) -> pd.DataFrame:

        return self.__getStats(
            variablesToQuery=tuple(getUnique(variablesToQuery)),
            forDomain=forDomain,
            inDomains=tuple(getUnique(inDomains)),
        )

    @cache
    def __getStats(
        self,
        variablesToQuery: Tuple[VariableCode],
        forDomain: GeoDomain,
        inDomains: Tuple[GeoDomain],
    ) -> pd.DataFrame:

        apiRes = self._api.stats(list(variablesToQuery), forDomain, list(inDomains))
        df = self._transformer.stats(apiRes, list(variablesToQuery))

        return df

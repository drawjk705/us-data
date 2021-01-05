from census.utils.cleanVariableName import cleanVariableName
from census.utils.timer import timer
from census.variables.repository.interface import IVariableRepository
from census.variables.models import VariableCode
from census.utils.unique import getUnique
from functools import cache
from typing import Any, Dict, List, Set, Tuple

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

    @timer
    def getStats(
        self,
        variablesToQuery: List[VariableCode],
        forDomain: GeoDomain,
        inDomains: List[GeoDomain] = [],
        replaceColumnHeaders: bool = False,
    ) -> pd.DataFrame:

        return self.__getStats(
            variablesToQuery=tuple(getUnique(variablesToQuery)),
            forDomain=forDomain,
            inDomains=tuple(getUnique(inDomains)),
            replaceColumnHeaders=replaceColumnHeaders,
        )

    @cache
    def __getStats(
        self,
        variablesToQuery: Tuple[VariableCode],
        forDomain: GeoDomain,
        inDomains: Tuple[GeoDomain],
        replaceColumnHeaders: bool = False,
    ) -> pd.DataFrame:

        pullStats = lambda: self._api.stats(
            list(variablesToQuery), forDomain, list(inDomains)
        )

        apiResults: List[List[List[str]]] = [res for res in pullStats()]

        columnHeaders, typeConversions = self._getVariableNamesAndTypeConversions(
            set(variablesToQuery)
        )

        df = self._transformer.stats(
            apiResults,
            typeConversions,
            [forDomain] + list(inDomains),
            columnHeaders=columnHeaders if replaceColumnHeaders else None,
        )

        return df

    def _getVariableNamesAndTypeConversions(
        self, variablesToQuery: Set[VariableCode]
    ) -> Tuple[Dict[VariableCode, str], Dict[str, Any]]:
        relevantVariables = {
            k: v
            for k, v in self._variableRepo.variables.items()
            if k in variablesToQuery
        }
        hasDuplicateNames = len({v.name for v in relevantVariables.values()}) < len(
            variablesToQuery
        )

        typeConversions: Dict[str, Any] = {}
        columnHeaders: Dict[VariableCode, str] = {}
        for k, v in relevantVariables.items():
            if v.predicateType == "float":
                typeConversions.update({k: float})
            elif v.predicateType == "int":
                typeConversions.update({k: int})

            cleanedVarName = cleanVariableName(v.name)
            if hasDuplicateNames:
                cleanedVarName += f"_{v.groupCode}"

            columnHeaders.update({k: cleanedVarName})

        return columnHeaders, typeConversions

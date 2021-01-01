from census.variableStorage.models import CodeSet, TGroupCode, TVariableCode
from functools import cache
from typing import Any, Dict, List, Tuple, Union

import pandas as pd
from census.api.interface import IApiFetchService
from census.dataCache.interface import ICache
from census.dataTransformation.interface import IDataTransformer
from census.models import GeoDomain
from census.utils.unique import getUnique
from census.variableStorage.interface import IVariableStorageService

GROUPS_FILE = "groups.csv"
SUPPORTED_GEOS_FILE = "supportedGeographies.csv"

VARIABLES_DIR = "variables"
QUERY_RESULTS_DIR = "queryResults"


class VariableStorageService(IVariableStorageService[pd.DataFrame]):

    _cache: ICache[pd.DataFrame]
    _api: IApiFetchService
    _transformer: IDataTransformer[pd.DataFrame]

    def __init__(
        self,
        cache: ICache[pd.DataFrame],
        transformer: IDataTransformer[pd.DataFrame],
        api: IApiFetchService,
    ):
        # these are inherited from the base class
        self.groupCodes = CodeSet[TGroupCode]()
        self.variableCodes = CodeSet[TVariableCode]()
        self._cache = cache
        self._api = api
        self._transformer = transformer

    def getGroups(self) -> pd.DataFrame:
        return self.__getGroups()

    @cache
    def __getGroups(self) -> pd.DataFrame:
        df = self._cache.get(GROUPS_FILE) or pd.DataFrame()

        if not df.any():  # type: ignore
            res = self._api.groupData()
            df = self._transformer.groups(res)

            self._cache.put(GROUPS_FILE, df)

        self._populateCodes(df, self.groupCodes, TGroupCode, "description")

        return df

    def getSupportedGeographies(self) -> pd.DataFrame:
        return self.__getSupportedGeographies()

    @cache
    def __getSupportedGeographies(self) -> pd.DataFrame:
        df = self._cache.get(SUPPORTED_GEOS_FILE) or pd.DataFrame()

        if not df.any():  # type: ignore
            res = self._api.supportedGeographies()
            df = self._transformer.supportedGeographies(res)

            self._cache.put(SUPPORTED_GEOS_FILE, df)

        return df

    def getGeographyCodes(
        self, forDomain: GeoDomain, inDomains: List[GeoDomain] = []
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

    def getVariablesByGroup(self, groups: List[TGroupCode]) -> pd.DataFrame:
        return self.__getVariablesByGroup(tuple(getUnique(groups)))

    @cache
    def __getVariablesByGroup(self, groups: Tuple[TGroupCode, ...]) -> pd.DataFrame:
        allVars = pd.DataFrame()

        for group in groups:
            resource = f"{VARIABLES_DIR}/{group}.csv"

            df = self._cache.get(resource) or pd.DataFrame()

            if df.any():  # type: ignore
                if not allVars.any():  # type: ignore
                    allVars = df
                else:
                    allVars.append(df, ignore_index=True)  # type: ignore
            else:
                res = self._api.variablesForGroup(group)
                df = self._transformer.variables(res)

                self._cache.put(resource, df)

                if not allVars.any():  # type: ignore
                    allVars = df
                else:
                    allVars.append(df, ignore_index=True)

        self._populateCodes(allVars, self.variableCodes, TVariableCode, "name")

        return allVars

    def _populateCodes(
        self,
        sourceDf: pd.DataFrame,
        codes: Union[CodeSet[TVariableCode], CodeSet[TGroupCode]],
        codeCtor: Any,
        meaningCol: str,
    ) -> None:
        codesList: List[Dict[str, str]] = sourceDf[["code", meaningCol]].to_dict(
            "records"
        )

        codes.addCodes(
            **{
                code["code"]: codeCtor(code["code"], code[meaningCol])
                for code in codesList
            }
        )

import logging
from census.variables.models import Code, CodeSet, TGroupCode, TVariableCode
from functools import cache
from typing import Any, Dict, List, Tuple, Union, cast

import pandas as pd
from census.api.interface import IApiFetchService
from census.variables.persistence.interface import ICache
from census.dataTransformation.interface import IDataTransformer
from census.models import GeoDomain
from census.utils.unique import getUnique
from census.variables.repository.interface import IVariableRepository

GROUPS_FILE = "groups.csv"
SUPPORTED_GEOS_FILE = "supportedGeographies.csv"

VARIABLES_DIR = "variables"
QUERY_RESULTS_DIR = "queryResults"

LOG_PREFIX = "[Variable Repository]"


class VariableRepository(IVariableRepository[pd.DataFrame]):

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
        df = self._cache.get(GROUPS_FILE)
        if df is None:
            df = pd.DataFrame()

        if df.empty:
            res = self._api.groupData()
            df = self._transformer.groups(res)

            self._cache.put(GROUPS_FILE, df)

        self._populateCodes(df, self.groupCodes, Code[TGroupCode], "description")

        return df

    def getSupportedGeographies(self) -> pd.DataFrame:
        return self.__getSupportedGeographies()

    @cache
    def __getSupportedGeographies(self) -> pd.DataFrame:
        df = self._cache.get(SUPPORTED_GEOS_FILE)

        if df is None:
            df = pd.DataFrame

        if df.empty:
            res = self._api.supportedGeographies()
            df = self._transformer.supportedGeographies(res)

            self._cache.put(SUPPORTED_GEOS_FILE, df)

        return cast(pd.DataFrame, df)

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

            df = self._cache.get(resource)
            if df is None:
                df = pd.DataFrame()

            if not df.empty:
                if allVars.empty:
                    allVars = df
                else:
                    allVars.append(df, ignore_index=True)  # type: ignore
            else:
                res = self._api.variablesForGroup(group)
                df = self._transformer.variables(res)

                self._cache.put(resource, df)

                if allVars.empty:
                    allVars = df
                else:
                    allVars.append(df, ignore_index=True)

        self._populateCodes(allVars, self.variableCodes, Code[TVariableCode], "name")

        return allVars

    def getAllVariables(self) -> pd.DataFrame:
        return self.__getAllVariables()

    @cache
    def __getAllVariables(self) -> pd.DataFrame:
        self.__log("This is a costly operation, and may take time")

        allGroups: List[str] = self.getGroups()["code"].to_list()  # type: ignore

        return self.getVariablesByGroup([TGroupCode(code) for code in allGroups])

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

    def __log(self, msg: str) -> None:
        logging.info(f"{LOG_PREFIX} {msg}")

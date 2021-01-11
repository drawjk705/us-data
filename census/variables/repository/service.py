import logging
from census.variables.repository.models import (
    GroupSet,
    VariableSet,
)
from census.utils.timer import timer
from functools import cache
from typing import Tuple, cast
from tqdm.notebook import tqdm

import pandas as pd
from census.api.interface import IApiFetchService
from census.dataTransformation.interface import IDataTransformer
from census.utils.unique import getUnique
from census.variables.models import Group, GroupVariable, GroupCode
from census.persistence.interface import ICache
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
        self._cache = cache
        self._api = api
        self._transformer = transformer

        # these are inherited from the base class
        self._variables = VariableSet()
        self._groups = GroupSet()

    @timer
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

        for record in df.to_dict("records"):
            group = Group.fromDfRecord(record)
            self._groups.add(group)

        return df

    @timer
    def getVariablesByGroup(self, *groups: GroupCode) -> pd.DataFrame:
        return self.__getVariablesByGroup(tuple(getUnique(groups)))

    @cache
    def __getVariablesByGroup(self, groups: Tuple[GroupCode, ...]) -> pd.DataFrame:
        allVars = pd.DataFrame()

        for group in tqdm(groups):  # type: ignore
            resource = f"{VARIABLES_DIR}/{group}.csv"

            df = self._cache.get(resource)
            if df is None:
                df = pd.DataFrame()

            if not df.empty:
                if allVars.empty:
                    allVars = df
                else:
                    allVars = allVars.append(df, ignore_index=True)  # type: ignore
            else:
                res = self._api.variablesForGroup(cast(GroupCode, group))
                df = self._transformer.variables(res)

                self._cache.put(resource, df)

                if allVars.empty:
                    allVars = df
                else:
                    allVars = allVars.append(df, ignore_index=True)

        for record in allVars.to_dict("records"):
            var = GroupVariable.fromDfRecord(record)
            self._variables.add(var)

        return allVars

    @timer
    def getAllVariables(self) -> pd.DataFrame:
        return self.__getAllVariables()

    @cache
    def __getAllVariables(self) -> pd.DataFrame:
        logging.info("This is a costly operation, and may take time")

        allVariables = self._api.allVariables()
        df = self._transformer.variables(allVariables)

        for groupCode, variables in df.groupby(["groupCode"]):  # type: ignore
            varDf = cast(pd.DataFrame, variables)
            if not self._cache.put(f"{VARIABLES_DIR}/{groupCode}.csv", varDf):
                # we don't need to update `self._variables` in this case
                continue

            for variableDict in varDf.to_dict("records"):
                variable = GroupVariable.fromDfRecord(variableDict)
                self._variables.add(variable)

        return df

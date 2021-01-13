import os
from functools import cache
from logging import Logger
from pathlib import Path
from typing import Tuple, cast

import pandas as pd
from census.api.interface import IApiFetchService
from census.dataTransformation.interface import IDataTransformer
from census.log.factory import ILoggerFactory
from census.persistence.interface import ICache
from census.utils.timer import timer
from census.utils.unique import getUnique
from census.variables.models import Group, GroupCode, GroupVariable
from census.variables.repository.interface import IVariableRepository
from census.variables.repository.models import GroupSet, VariableSet
from tqdm.notebook import tqdm

GROUPS_FILE = "groups.csv"
SUPPORTED_GEOS_FILE = "supportedGeographies.csv"

VARIABLES_DIR = "variables"


class VariableRepository(IVariableRepository[pd.DataFrame]):

    _cache: ICache[pd.DataFrame]
    _api: IApiFetchService
    _transformer: IDataTransformer[pd.DataFrame]
    _logger: Logger

    def __init__(
        self,
        cache: ICache[pd.DataFrame],
        transformer: IDataTransformer[pd.DataFrame],
        api: IApiFetchService,
        loggerFactory: ILoggerFactory,
    ):
        self._cache = cache
        self._api = api
        self._transformer = transformer
        self._logger = loggerFactory.getLogger(__name__)

        # these are inherited from the base class
        self._variables = VariableSet()
        self._groups = GroupSet()

        self.__populateRepository()

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

        groups = [Group.fromDfRecord(rec) for rec in df.to_dict("records")]
        self._groups.add(*groups)

        return df.drop(columns=["cleanedName"])  # type: ignore

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

        return allVars.drop(columns=["cleanedName"])  # type: ignore

    @timer
    def getAllVariables(self) -> pd.DataFrame:
        return self.__getAllVariables()

    @cache
    def __getAllVariables(self) -> pd.DataFrame:
        self._logger.info("This is a costly operation, and may take time")

        allVariables = self._api.allVariables()
        df = self._transformer.variables(allVariables)

        for groupCode, variables in df.groupby(["groupCode"]):  # type: ignore
            varDf = cast(pd.DataFrame, variables)

            if not self._cache.put(f"{VARIABLES_DIR}/{groupCode}.csv", varDf):
                # we don't need to update `self._variables` in this case
                continue

            variables = [
                GroupVariable.fromDfRecord(record)
                for record in varDf.to_dict("records")
            ]
            self._variables.add(*variables)

        return df.drop(columns=["cleanedName"])  # type: ignore

    def __populateRepository(self) -> None:
        self._logger.debug("populating repository")

        groupsDf = self._cache.get(GROUPS_FILE)

        if groupsDf is not None:
            groups = [
                Group.fromDfRecord(record) for record in groupsDf.to_dict("records")
            ]
            self._logger.debug(f"adding groups {[group.code for group in groups]}")
            self._groups.add(*groups)

        variablesPath = f"{self._cache.cachePath}/{VARIABLES_DIR}"

        if not Path(variablesPath).exists():
            self._logger.debug("no variables")
            return

        for file in os.listdir(variablesPath):
            cacheRes = self._cache.get(f"{VARIABLES_DIR}/{file}")
            variableDf = cacheRes if cacheRes is not None else pd.DataFrame()

            self._logger.debug(f"adding variables from {file}")

            variables = [
                GroupVariable.fromDfRecord(record)
                for record in variableDf.to_dict("records")
            ]
            self._variables.add(*variables)

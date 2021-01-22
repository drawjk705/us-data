import os
from functools import cache
from logging import Logger
from pathlib import Path
from typing import Tuple, cast

import pandas as pd
from tqdm.notebook import tqdm

from the_census._api.interface import ICensusApiFetchService
from the_census._data_transformation.interface import ICensusDataTransformer
from the_census._persistence.interface import ICache
from the_census._utils.log.factory import ILoggerFactory
from the_census._utils.timer import timer
from the_census._utils.unique import get_unique
from the_census._variables.models import Group, GroupCode, GroupVariable
from the_census._variables.repository.interface import IVariableRepository
from the_census._variables.repository.models import GroupSet, VariableSet

GROUPS_FILE = "groups.csv"
SUPPORTED_GEOS_FILE = "supported_geographies.csv"

VARIABLES_DIR = "variables"


class VariableRepository(IVariableRepository[pd.DataFrame]):

    _cache: ICache[pd.DataFrame]
    _api: ICensusApiFetchService
    _transformer: ICensusDataTransformer[pd.DataFrame]
    _logger: Logger

    def __init__(
        self,
        cache: ICache[pd.DataFrame],
        transformer: ICensusDataTransformer[pd.DataFrame],
        api: ICensusApiFetchService,
        logger_factory: ILoggerFactory,
    ):
        self._cache = cache
        self._api = api
        self._transformer = transformer
        self._logger = logger_factory.getLogger(__name__)

        # these are inherited from the base class
        self._variables = VariableSet()
        self._groups = GroupSet()

        self.__populate_repository()

    @timer
    def get_groups(self) -> pd.DataFrame:
        return self.__get_groups()

    @cache
    def __get_groups(self) -> pd.DataFrame:
        df = self._cache.get(GROUPS_FILE)
        if df is None:
            df = pd.DataFrame()

        if df.empty:
            res = self._api.group_data()

            if len(res) == 0:
                return pd.DataFrame()

            df = self._transformer.groups(res)

            self._cache.put(GROUPS_FILE, df)

        groups = [Group.from_df_record(rec) for rec in df.to_dict("records")]
        self._groups.add(*groups)

        return df.drop(columns=["cleaned_name"])  # type: ignore

    @timer
    def get_variables_by_group(self, *groups: GroupCode) -> pd.DataFrame:
        return self.__get_variables_by_group(tuple(get_unique(groups)))

    @cache
    def __get_variables_by_group(self, groups: Tuple[GroupCode, ...]) -> pd.DataFrame:
        all_vars = pd.DataFrame()

        for group in tqdm(groups):  # type: ignore
            resource = f"{VARIABLES_DIR}/{group}.csv"

            df = self._cache.get(resource)
            if df is None:
                df = pd.DataFrame()

            if not df.empty:
                if all_vars.empty:
                    all_vars = df
                else:
                    all_vars = all_vars.append(df, ignore_index=True)  # type: ignore
            else:
                res = self._api.variables_for_group(cast(GroupCode, group))

                if len(res) == 0:
                    continue

                df = self._transformer.variables(res)

                self._cache.put(resource, df)

                if all_vars.empty:
                    all_vars = df
                else:
                    all_vars = all_vars.append(df, ignore_index=True)

        if all_vars.empty:
            return pd.DataFrame()

        for record in all_vars.to_dict("records"):
            var = GroupVariable.from_df_record(record)
            self._variables.add(var)

        return all_vars.drop(columns=["cleaned_name"])  # type: ignore

    @timer
    def get_all_variables(self) -> pd.DataFrame:
        return self.__get_all_variables()

    @cache
    def __get_all_variables(self) -> pd.DataFrame:
        self._logger.info("This is a costly operation, and may take time")

        all_variables = self._api.all_variables()

        if len(all_variables) == 0:
            return pd.DataFrame()

        df = self._transformer.variables(all_variables)

        for GroupCode, variables in df.groupby(["group_code"]):  # type: ignore
            varDf = cast(pd.DataFrame, variables)

            if not self._cache.put(f"{VARIABLES_DIR}/{GroupCode}.csv", varDf):
                # we don't need to update `self._variables` in this case
                continue

            variables = [
                GroupVariable.from_df_record(record)
                for record in varDf.to_dict("records")
            ]
            self._variables.add(*variables)

        return df.drop(columns=["cleaned_name"])  # type: ignore

    def __populate_repository(self) -> None:
        self._logger.debug("populating repository")

        groups_df = self._cache.get(GROUPS_FILE)

        if groups_df is not None:
            groups = [
                Group.from_df_record(record) for record in groups_df.to_dict("records")
            ]
            self._logger.debug(f"adding groups {[group.code for group in groups]}")
            self._groups.add(*groups)

        variables_path = f"{self._cache.cache_path}/{VARIABLES_DIR}"

        if not Path(variables_path).exists():
            self._logger.debug("no variables")
            return

        for file in os.listdir(variables_path):
            cache_res = self._cache.get(f"{VARIABLES_DIR}/{file}")
            variable_df = cache_res if cache_res is not None else pd.DataFrame()

            self._logger.debug(f"adding variables from {file}")

            variables = [
                GroupVariable.from_df_record(record)
                for record in variable_df.to_dict("records")
            ]
            self._variables.add(*variables)

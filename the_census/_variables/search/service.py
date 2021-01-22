from logging import Logger

import pandas as pd

from the_census._utils.log.factory import ILoggerFactory
from the_census._utils.timer import timer
from the_census._variables.models import GroupCode
from the_census._variables.repository.interface import IVariableRepository
from the_census._variables.search.interface import IVariableSearchService


class VariableSearchService(IVariableSearchService[pd.DataFrame]):
    _variable_repository: IVariableRepository[pd.DataFrame]
    _logger: Logger

    def __init__(
        self,
        variableRepository: IVariableRepository[pd.DataFrame],
        loggerFactory: ILoggerFactory,
    ) -> None:
        self._variable_repository = variableRepository
        self._logger = loggerFactory.getLogger(__name__)

    @timer
    def search_groups(self, regex: str) -> pd.DataFrame:
        self._logger.debug(f"searching groups for regex: `{regex}`")

        groups = self._variable_repository.get_groups()

        if groups.empty:
            self._logger.info("There are no groups for this dataset")

            return pd.DataFrame()

        series: pd.Series[bool] = groups["description"].str.contains(  # type: ignore
            regex, case=False
        )

        return groups[series].reset_index(
            drop=True,
        )

    @timer
    def search_variables(
        self,
        regex: str,
        *in_groups: GroupCode,
    ) -> pd.DataFrame:

        self._logger.debug(f"searching variables for pattern `{regex}`")

        variables: pd.DataFrame
        if not len(in_groups):
            variables = self._variable_repository.get_all_variables()
        else:
            variables = self._variable_repository.get_variables_by_group(*in_groups)

        if variables.empty:
            self._logger.info("There are no variables for this dataset")
            return pd.DataFrame()

        series = variables["name"].str.contains(regex, case=False)  # type: ignore

        return variables[series].reset_index(drop=True)  # type: ignore

from logging import Logger

import pandas as pd

from us_data.census.variables.models import GroupCode
from us_data.census.variables.repository.interface import IVariableRepository
from us_data.census.variables.search.interface import IVariableSearchService
from us_data.utils.log.factory import ILoggerFactory
from us_data.utils.timer import timer


class VariableSearchService(IVariableSearchService[pd.DataFrame]):
    _variableRepository: IVariableRepository[pd.DataFrame]
    _logger: Logger

    def __init__(
        self,
        variableRepository: IVariableRepository[pd.DataFrame],
        loggerFactory: ILoggerFactory,
    ) -> None:
        self._variableRepository = variableRepository
        self._logger = loggerFactory.getLogger(__name__)

    @timer
    def searchGroups(self, regex: str) -> pd.DataFrame:
        self._logger.debug(f"searching groups for regex: `{regex}`")

        groups = self._variableRepository.getGroups()

        series: pd.Series[bool] = groups["description"].str.contains(  # type: ignore
            regex, case=False
        )

        return groups[series].reset_index(
            drop=True,
        )

    @timer
    def searchVariables(
        self,
        regex: str,
        *inGroups: GroupCode,
    ) -> pd.DataFrame:

        self._logger.debug(f"searching variables for pattern `{regex}`")

        variables: pd.DataFrame
        if not len(inGroups):
            variables = self._variableRepository.getAllVariables()
        else:
            variables = self._variableRepository.getVariablesByGroup(*inGroups)

        series = variables["name"].str.contains(regex, case=False)  # type: ignore

        return variables[series].reset_index(drop=True)  # type: ignore

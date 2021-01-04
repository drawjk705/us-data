from census.utils.timer import timer
from census.variables.repository.interface import IVariableRepository
from census.variables.search.interface import IVariableSearchService
from census.variables.models import GroupCode
from typing import List, Literal
import pandas as pd

import logging


class VariableSearchService(IVariableSearchService[pd.DataFrame]):
    _variableRepository: IVariableRepository[pd.DataFrame]

    def __init__(self, variableRepository: IVariableRepository[pd.DataFrame]) -> None:
        self._variableRepository = variableRepository

    @timer
    def searchGroups(self, regex: str) -> pd.DataFrame:
        logging.info(f"searching groups for regex: `{regex}`")

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
        searchBy: Literal["name", "concept"] = "name",
        inGroups: List[GroupCode] = [],
    ) -> pd.DataFrame:
        if searchBy not in ["name", "concept"]:
            raise Exception('searchBy parameter must be "name" or "concept"')

        logging.info(f"searching variables for pattern `{regex}` by {searchBy}")

        variables: pd.DataFrame
        if not len(inGroups):
            variables = self._variableRepository.getAllVariables()
        else:
            variables = self._variableRepository.getVariablesByGroup(inGroups)

        series = variables[searchBy].str.contains(regex, case=False)  # type: ignore

        return variables[series]  # type: ignore

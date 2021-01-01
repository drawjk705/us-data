from census.variableStorage.models import TGroupCode
from census.variableStorage.interface import IVariableStorageService
from typing import List, Literal
import pandas as pd

import logging

from census.variableSearch.interface import IVariableSearchService


class VariableSearchService(IVariableSearchService[pd.DataFrame]):
    _variableStorage: IVariableStorageService[pd.DataFrame]

    def __init__(self, variableStorage: IVariableStorageService[pd.DataFrame]) -> None:
        self._variableStorage = variableStorage

    def searchGroups(self, regex: str) -> pd.DataFrame:
        logging.info(f"searching groups for regex: `{regex}`")

        groups = self._variableStorage.getGroups()

        series: pd.Series[bool] = groups["description"].str.contains(  # type: ignore
            regex, case=False
        )

        return groups[series]

    def searchVariables(
        self,
        regex: str,
        searchBy: Literal["name", "concept"] = "name",
        inGroups: List[TGroupCode] = [],
    ) -> pd.DataFrame:
        if searchBy not in ["name", "concept"]:
            raise Exception('searchBy parameter must be "name" or "concept"')

        logging.info(f"searching variables for pattern `{regex}` by {searchBy}")

        variables = self._variableStorage.getVariablesByGroup(inGroups)

        series = variables[searchBy].str.contains(regex, case=False)  # type: ignore

        return variables[series]  # type: ignore
from census.models import GeoDomain
from census.variables.models import Group, GroupVariable, GroupCode, VariableCode
from typing import Dict, List, Literal
from census.variables.repository.interface import IVariableRepository
from census.variables.search.interface import IVariableSearchService
from census.stats.interface import ICensusStatisticsService
import pandas as pd


class Census:

    _variableRepo: IVariableRepository[pd.DataFrame]
    _variableSearch: IVariableSearchService[pd.DataFrame]
    _stats: ICensusStatisticsService[pd.DataFrame]

    variables: Dict[VariableCode, GroupVariable]
    groups: Dict[GroupCode, Group]

    def __init__(
        self,
        variableRepo: IVariableRepository[pd.DataFrame],
        variableSearch: IVariableSearchService[pd.DataFrame],
        stats: ICensusStatisticsService[pd.DataFrame],
    ) -> None:
        self._variableRepo = variableRepo
        self._variableSearch = variableSearch
        self._stats = stats

    # search
    def searchGroups(self, regex: str) -> pd.DataFrame:
        return self._variableSearch.searchGroups(regex)

    def searchVariables(
        self,
        regex: str,
        searchBy: Literal["name", "concept"] = "name",
        inGroups: List[GroupCode] = [],
    ) -> pd.DataFrame:
        return self._variableSearch.searchVariables(regex, searchBy, inGroups)

    # repo
    def getGeographyCodes(
        self, forDomain: GeoDomain, inDomains: List[GeoDomain] = []
    ) -> pd.DataFrame:
        return self._variableRepo.getGeographyCodes(forDomain, inDomains)

    def getGroups(self) -> pd.DataFrame:
        groups = self._variableRepo.getGroups()
        self.groups = self._variableRepo.groups
        return groups

    def getVariablesByGroup(self, groups: List[GroupCode]) -> pd.DataFrame:
        variables = self._variableRepo.getVariablesByGroup(groups)
        self.variables = self._variableRepo.variables
        return variables

    def getAllVariables(self) -> pd.DataFrame:
        variables = self._variableRepo.getAllVariables()
        self.variables = self._variableRepo.variables
        return variables

    def getSupportedGeographies(self) -> pd.DataFrame:
        return self._variableRepo.getSupportedGeographies()

    # stats
    def getStats(
        self,
        variablesToQuery: List[VariableCode],
        forDomain: GeoDomain,
        inDomains: List[GeoDomain] = [],
    ) -> pd.DataFrame:
        return self._stats.getStats(variablesToQuery, forDomain, inDomains)

from census.geographies.models import SupportedGeoSet
from census.geographies.interface import IGeographyRepository
from census.variables.repository.models import GroupSet, GroupToVarsMapping, VariableSet
from typing import List, Literal

import pandas as pd

from census.api.fetch import IApiFetchService
from census.models import GeoDomain
from census.stats.interface import ICensusStatisticsService
from census.variables.models import GroupCode, VariableCode
from census.variables.repository.interface import IVariableRepository
from census.variables.search.interface import IVariableSearchService


class Census:
    """
    The Census client. This is what users will be interacting with.
    """

    _variableRepo: IVariableRepository[pd.DataFrame]
    _variableSearch: IVariableSearchService[pd.DataFrame]
    _stats: ICensusStatisticsService[pd.DataFrame]
    _geoRepo: IGeographyRepository[pd.DataFrame]

    def __init__(
        self,
        variableRepo: IVariableRepository[pd.DataFrame],
        variableSearch: IVariableSearchService[pd.DataFrame],
        stats: ICensusStatisticsService[pd.DataFrame],
        api: IApiFetchService,
        geoRepo: IGeographyRepository[pd.DataFrame],
    ) -> None:
        self._variableRepo = variableRepo
        self._variableSearch = variableSearch
        self._stats = stats
        self._geoRepo = geoRepo

        # if this healthcheck fails, it will throw, and we
        # won't instantiate the client
        api.healthCheck()

    # search
    def searchGroups(self, regex: str) -> pd.DataFrame:
        """
        Searches all group's based on their concept, according
        to `regex`

        Args:
            regex (str)

        Returns:
            pd.DataFrame: with all of the relevant groups.
        """
        return self._variableSearch.searchGroups(regex)

    def searchVariables(
        self,
        regex: str,
        searchBy: Literal["name", "concept"] = "name",
        *inGroups: GroupCode,
    ) -> pd.DataFrame:
        """
        - Searches variables based on `regex`.
        - It can search variables based on their name or group concept.
        - Specify `inGroups` with a list of group codes to restrict the search to
        variables within a particular group, or leave it empty to search all variables.
        - This will pull from the API whatever variables aren't in memory.

        Args:
            regex (str)
            searchBy (Literal[, optional): whether to search based on
            the variables' names or group concepts. Defaults to "name".
            inGroups (List[GroupCode], optional): if populated, this will search
            only the variables within the specified groups. Defaults to [].

        Returns:
            pd.DataFrame: with all of the matched variables
        """
        return self._variableSearch.searchVariables(regex, searchBy, *inGroups)

    # repo
    def getGeographyCodes(
        self, forDomain: GeoDomain, *inDomains: GeoDomain
    ) -> pd.DataFrame:
        """
        Gets geography codes for the specified geography query.
        A GeoDomain is comprised of the domain (e.g., "state"), and an ID
        or wildcard. So passing in a `forDomain` of GeoDomain("congressional district", "*")
        would get all geography codes for all congressional district; providing an `inDomain`
        of, [GeoDomain("state", "06")] would constrain that search to the state with ID
        06 (California).

        Args:
            forDomain (GeoDomain): the primary geography region to query
            inDomains (List[GeoDomain], optional): any parents of the `forDomain`.
            Whether or not these must be populated and/or can have wildcards
            depends on the dataset/survey's supported geographies. (See `supportedGeographies`
            below.). Defaults to [].

        Returns:
            pd.DataFrame: [description]
        """
        return self._geoRepo.getGeographyCodes(forDomain, *inDomains)

    def getGroups(self) -> pd.DataFrame:
        """
        Gets all groups for the dataset/survey

        Returns:
            pd.DataFrame: with all of the groups
        """
        return self._variableRepo.getGroups()

    def getVariablesByGroup(self, *groups: GroupCode) -> pd.DataFrame:
        """
        Gets all variables whose group is in `groups`.

        Args:
            groups (List[GroupCode]): codes of all the groups whose variables you want.

        Returns:
            pd.DataFrame: with the queried variables.
        """
        return self._variableRepo.getVariablesByGroup(*groups)

    def getAllVariables(self) -> pd.DataFrame:
        """
        Gets all variables available to the dataset/survey.
        This may take a while.

        Returns:
            pd.DataFrame: with all of the variables.
        """
        return self._variableRepo.getAllVariables()

    def getSupportedGeographies(self) -> pd.DataFrame:
        """
        Returns a DataFrame with all possible geography query
        patterns for the given dataset/survey.

        Returns:
            pd.DataFrame
        """
        return self._geoRepo.getSupportedGeographies()

    # stats
    def getStats(
        self,
        variablesToQuery: List[VariableCode],
        forDomain: GeoDomain,
        inDomains: List[GeoDomain] = [],
        replaceColumnHeaders: bool = False,
    ) -> pd.DataFrame:
        """
        Gets statistical data based on `variablesToQuery`
        for the specified geographies.

        Args:
            variablesToQuery (List[VariableCode]): the variables to query
            forDomain (GeoDomain)
            inDomains (List[GeoDomain], optional): Defaults to [].
            replaceColumnHeaders (bool, optional): if `True`, this will
            replace all column headers in the resulting DataFrame with the variables'
            names, as opposed to their codes. Defaults to False.

        Returns:
            pd.DataFrame: with the data
        """
        return self._stats.getStats(
            variablesToQuery, forDomain, inDomains, replaceColumnHeaders
        )

    @property
    def variables(self) -> VariableSet:
        return self._variableRepo.variables

    @property
    def groups(self) -> GroupSet:
        return self._variableRepo.groups

    @property
    def groupToVarsMapping(self) -> GroupToVarsMapping:
        return self._variableRepo.groupToVarsMapping

    @property
    def supportedGeographies(self) -> SupportedGeoSet:
        return self._geoRepo.supportedGeographies
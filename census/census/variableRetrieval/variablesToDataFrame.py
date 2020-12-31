from census.utils.unique import getUnique
from census.models import GeoDomain
from census.dataTransformation.IDataTransformer import IDataTransformer
from census.api.fetch import ApiFetchService
from census.variableRetrieval.ICache import ICache
from census.variableRetrieval.IVariableRetrievalService import IVariableRetrievalService
from functools import cache
from typing import Dict, List, Tuple

import pandas as pd
from census.variableRetrieval.models import VariableCode, VariableCodes

GROUPS_FILE = "groups.csv"
SUPPORTED_GEOS_FILE = "supportedGeographies.csv"

VARIABLES_DIR = "variables"
QUERY_RESULTS_DIR = "queryResults"


class VariablesToDataFrameService(IVariableRetrievalService[pd.DataFrame]):

    __cache: ICache[pd.DataFrame]
    __api: ApiFetchService
    __transformer: IDataTransformer[pd.DataFrame]

    def __init__(
        self,
        cache: ICache[pd.DataFrame],
        transformer: IDataTransformer[pd.DataFrame],
        api: ApiFetchService,
    ):
        # these are inherited from the base class
        self.groupCodes = VariableCodes()
        self.variableCodes = VariableCodes()
        self.__cache = cache
        self.__api = api
        self.__transformer = transformer

    def getGroups(self) -> pd.DataFrame:
        return self.__getGroups()

    @cache
    def __getGroups(self) -> pd.DataFrame:
        df = self.__cache.get(GROUPS_FILE) or pd.DataFrame()

        if df.empty:
            res = self.__api.groupData()
            df = self.__transformer.groups(res)

            self.__cache.put(GROUPS_FILE, df)

        self._populateCodes(df, self.groupCodes, "description")

        return df

    def getSupportedGeographies(self) -> pd.DataFrame:
        return self.__getSupportedGeographies()

    @cache
    def __getSupportedGeographies(self) -> pd.DataFrame:
        df = self.__cache.get(SUPPORTED_GEOS_FILE) or pd.DataFrame()

        if df.empty:
            res = self.__api.supportedGeographies()
            df = self.__transformer.supportedGeographies(res)

            self.__cache.put(SUPPORTED_GEOS_FILE, df)

        return df

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
        res = self.__api.geographyCodes(forDomain, list(inDomains))
        df = self.__transformer.geographyCodes(res)
        return df

    def getVariablesByGroup(self, groups: List[str]) -> pd.DataFrame:
        return self.__getVariablesByGroup(tuple(getUnique(groups)))

    @cache
    def __getVariablesByGroup(self, groups: Tuple[str, ...]) -> pd.DataFrame:
        allVars = pd.DataFrame()

        for group in groups:
            resource = f"{VARIABLES_DIR}/{group}.csv"

            df = self.__cache.get(resource) or pd.DataFrame()

            if not df.empty:
                if allVars.empty:  # type: ignore
                    allVars = df
                else:
                    allVars.append(df, ignore_index=True)  # type: ignore
            else:
                res = self.__api.variables(group)
                df = self.__transformer.variables(res)

                self.__cache.put(resource, df)

                if allVars.empty:
                    allVars = df
                else:
                    allVars.append(df, ignore_index=True)

        self._populateCodes(allVars, self.variableCodes, "name")

        return allVars

    # def searchGroups(self, regex: str) -> pd.DataFrame:
    #     logging.info(f"searching groups for pattern {regex}")

    #     groups = self.getGroups()

    #     series: pd.Series = groups["description"].str.contains(  # type: ignore
    #         regex, case=False
    #     )

    #     return groups[series]

    # def searchVariables(
    #     self,
    #     regex: str,
    #     searchBy: Literal["name", "concept"] = "name",
    #     inGroups: List[str] = [],
    # ) -> pd.DataFrame:
    #     if searchBy not in ["name", "concept"]:
    #         raise Exception('searchBy parameter must be "name" or "concept"')

    #     logging.info(f"searching variables for pattern `{regex}` by {searchBy}")

    #     variables = self.getVariablesByGroup(inGroups)

    #     series = variables[searchBy].str.contains(regex, case=False)  # type: ignore

    #     return variables[series]  # type: ignore

    def _populateCodes(
        self, sourceDf: pd.DataFrame, codes: VariableCodes, meaningCol: str
    ) -> None:
        codesList: List[Dict[str, str]] = sourceDf[["code", meaningCol]].to_dict(
            "records"
        )

        codes.addCodes(
            **{
                code["code"]: VariableCode(code["code"], code[meaningCol])
                for code in codesList
            }
        )

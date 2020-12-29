import logging
from functools import cache
from pathlib import Path
from typing import Dict, List, Literal, Tuple

import pandas as pd
from api.ApiConfig import ApiConfig
from models import DatasetType, GeoDomain, SurveyType

from variableRetrieval import OnDiskCache, VariableCode, VariableCodes
import variableRetrieval.utils as retUtils

GROUPS_FILE = 'groups.csv'
SUPPORTED_GEOS_FILE = 'supportedGeographies.csv'

VARIABLES_DIR = 'variables'
QUERY_RESULTS_DIR = 'queryResults'


class VariableRetriever:
    datasetType: DatasetType
    surveyType: SurveyType
    year: int

    # these will be useful for jupyter
    variableCodes: VariableCodes
    groupCodes: VariableCodes

    __onDiskCache: OnDiskCache

    __apiConfig: ApiConfig

    def __init__(self,
                 year: int,
                 datasetType: DatasetType = DatasetType.ACS,
                 surveyType: SurveyType = SurveyType.ACS1,
                 shouldLoadFromExistingCache: bool = False):
        self.year = year
        self.datasetType = datasetType
        self.surveyType = surveyType

        self.__apiConfig = ApiConfig(year, datasetType, surveyType)

        self.groupCodes = VariableCodes()
        self.variableCodes = VariableCodes()

        self.__onDiskCache = OnDiskCache(
            year=year,
            datasetType=datasetType,
            surveyType=surveyType,
            shouldLoadFromExistingCache=shouldLoadFromExistingCache)

        logging.info(
            f'Ready to retrieve census data for the {surveyType.upper()}-{year}')

    def getGroups(self) -> pd.DataFrame:
        return self.__getGroups()

    @cache
    def __getGroups(self) -> pd.DataFrame:
        groupsPath = Path(GROUPS_FILE)

        groups = self.__onDiskCache.getFromCache(groupsPath)

        if groups.empty:
            groups = retUtils.getGroups(self.__apiConfig)

            self.__onDiskCache.persist(groupsPath, groups)

        self.__populateCodes(groups, self.groupCodes, "description")

        return groups

    def getSupportedGeographies(self) -> pd.DataFrame:
        return self.__getSupportedGeographies()

    @cache
    def __getSupportedGeographies(self) -> pd.DataFrame:
        supportedGeographies = self.__onDiskCache.getFromCache(
            Path(SUPPORTED_GEOS_FILE))

        if supportedGeographies.empty:
            supportedGeographies = retUtils.getSupportedGeographies(
                self.__apiConfig)

            self.__onDiskCache.persist(Path(SUPPORTED_GEOS_FILE),
                                       supportedGeographies)

        return supportedGeographies

    def getGeographyCodes(self, forDomain: GeoDomain, inDomains: List[GeoDomain] = []) -> pd.DataFrame:
        return self.__getGeographyCodes(forDomain, inDomains=tuple(inDomains))

    @ cache
    def __getGeographyCodes(self, forDomain: GeoDomain, inDomains: Tuple[GeoDomain, ...] = ()) -> pd.DataFrame:
        return retUtils.getGeographyCodes(self.__apiConfig, forDomain, list(inDomains))

    def getVariablesByGroup(self, groups: List[str]) -> pd.DataFrame:
        return self.__getVariablesByGroup(tuple(groups))

    @ cache
    def __getVariablesByGroup(self, groups: Tuple[str, ...]) -> pd.DataFrame:
        allVars = pd.DataFrame()

        for group in groups:
            file = Path(f'{group}.csv')
            parentPath = Path(VARIABLES_DIR)
            fullPath = parentPath / file

            df = self.__onDiskCache.getFromCache(file, parentPath)

            if not df.empty:
                if allVars.empty:
                    allVars = df
                else:
                    allVars.append(df, ignore_index=True)
            else:
                df = retUtils.getVariables(group, self.__apiConfig)

                self.__onDiskCache.persist(fullPath, df)

                if allVars.empty:
                    allVars = df
                else:
                    allVars.append(df, ignore_index=True)

        self.__populateCodes(allVars, self.variableCodes, "name")

        return allVars

    def searchGroups(self, regex: str) -> pd.DataFrame:
        logging.info(f'searching groups for pattern {regex}')

        groups = self.getGroups()

        series: pd.Series = groups['description'].str.contains(  # type: ignore
            regex, case=False)

        return groups[series]

    def searchVariables(self,
                        regex: str,
                        searchBy: Literal['name', 'concept'] = 'name',
                        inGroups: List[str] = []) -> pd.DataFrame:
        if searchBy not in ['name', 'concept']:
            raise Exception('searchBy parameter must be "name" or "concept"')

        logging.info(
            f'searching variables for pattern `{regex}` by {searchBy}')

        variables = self.getVariablesByGroup(inGroups)

        series = variables[searchBy].str.contains(  # type: ignore
            regex, case=False)

        return variables[series]  # type: ignore

    def __populateCodes(self, sourceDf: pd.DataFrame, codes: VariableCodes, meaningCol: str) -> None:
        codesList: List[Dict[str, str]] = sourceDf[[
            'code', meaningCol]].to_dict('records')

        codes.addCodes(  # type: ignore
            **{
                code['code']: VariableCode(code['code'], code[meaningCol])
                for code in codesList
            })

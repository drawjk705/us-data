import logging
from functools import cache
from pathlib import Path
from typing import Dict, List, Literal, Tuple

import pandas as pd
from api.ApiConfig import ApiConfig
from api.models.Domain import Domain
from models.DatasetType import DatasetType
from models.SurveyType import SurveyType

from variableRetrieval.getGroups import getGroups
from variableRetrieval.getGeographyCodes import getGeographyCodes
from variableRetrieval.getSupportedGeographies import getSupportedGeographies
from variableRetrieval.getVariables import getVariables
from variableRetrieval.OnDiskCache import OnDiskCache


class _Code:
    code: str
    meaning: str

    def __init__(self, code: str, meaning: str) -> None:
        self.code = code
        self.meaning = meaning

    def __repr__(self) -> str:
        return self.__dict__.__repr__()


class _Codes:
    def __init__(self, **kwargs: dict) -> None:  # type: ignore
        for k, v in kwargs.items():
            self.__setattr__(k, v)  # type: ignore

    def addCodes(self, **codes: dict) -> None:  # type: ignore
        for k, v in codes.items():
            self.__setattr__(k, v)  # type: ignore

    def __repr__(self) -> str:
        return self.__dict__.__repr__()


GROUPS_FILE = 'groups.csv'
SUPPORTED_GEOS_FILE = 'supportedGeographies.csv'

VARIABLES_DIR = 'variables'
GEOGRAPHY_CODES_DIR = 'geographyCodes'
QUERY_RESULTS_DIR = 'queryResults'


class VariableRetriever:
    datasetType: DatasetType
    surveyType: SurveyType
    year: int

    # these will be useful for jupyter
    variableCodes: _Codes
    groupCodes: _Codes

    __cache: OnDiskCache

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

        self.groupCodes = _Codes()
        self.variableCodes = _Codes()

        self.__cache = OnDiskCache(
            year=year,
            datasetType=datasetType,
            surveyType=surveyType,
            shouldLoadFromExistingCache=shouldLoadFromExistingCache)

    @cache
    def getGroups(self) -> pd.DataFrame:
        groupsPath = Path(GROUPS_FILE)

        groups = self.__cache.getFromCache(groupsPath)

        if groups.empty:
            groups = getGroups(self.__apiConfig)

            self.__cache.persist(groupsPath, groups)

        self.__populateCodes(groups, self.groupCodes, "description")

        return groups

    @cache
    def getSupportedGeographies(self) -> pd.DataFrame:
        supportedGeographies = self.__cache.getFromCache(
            Path(SUPPORTED_GEOS_FILE))

        if supportedGeographies.empty:
            supportedGeographies = getSupportedGeographies(self.__apiConfig)
            self.__cache.persist(Path(SUPPORTED_GEOS_FILE),
                                 supportedGeographies)

        return supportedGeographies

    @cache
    def getGeographyCodes(self, forDomain: Domain, inDomains: Tuple[Domain, ...] = ()) -> pd.DataFrame:
        return getGeographyCodes(self.__apiConfig, forDomain, list(inDomains))

    def getVariablesByGroup(self, groups: List[str]) -> pd.DataFrame:
        allVars: pd.DataFrame = pd.DataFrame()

        for group in groups:
            file = Path(f'{group}.csv')
            parentPath = Path(VARIABLES_DIR)
            fullPath = parentPath / file

            df = self.__cache.getFromCache(file, parentPath)

            if not df.empty:
                if allVars.empty:
                    allVars = df
                else:
                    allVars.append(df, ignore_index=True)
            else:
                df = getVariables(group, self.__apiConfig)

                self.__cache.persist(fullPath, df)

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

    def __populateCodes(self, sourceDf: pd.DataFrame, codes: _Codes, meaningCol: str) -> None:
        codesList: List[Dict[str, str]] = sourceDf[[
            'code', meaningCol]].to_dict('records')

        codes.addCodes(  # type: ignore
            **{
                code['code']: _Code(code['code'], code[meaningCol])
                for code in codesList
            })

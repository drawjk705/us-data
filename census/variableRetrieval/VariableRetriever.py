from typing import Literal, List, Dict
from variableRetrieval.getVariables import getVariables
from variableRetrieval.getGroups import getGroups
from variableRetrieval.getGeographies import getGeographies
import pandas as pd
from models.SurveyType import SurveyType
from models.DatasetType import DatasetType
from variableRetrieval.VariableRetrievalCache import VariableRetrievalCache
import logging


class _Code:
    code: str
    meaning: str

    def __init__(self, code: str, meaning: str) -> None:
        self.code = code
        self.meaning = meaning

    def __repr__(self) -> str:
        return self.__dict__.__repr__()


class _Codes:
    def __init__(self, **kwargs: dict) -> None:
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def addCodes(self, **codes: dict) -> None:
        for k, v in codes.items():
            self.__setattr__(k, v)

    def __repr__(self) -> str:
        return self.__dict__.__repr__()


class VariableRetriever:
    datasetType: DatasetType
    surveyType: SurveyType
    year: str

    # these will be useful for jupyter
    variableCodes: _Codes
    groupCodes: _Codes

    __cache: VariableRetrievalCache

    def __init__(self,
                 year: int,
                 datasetType: DatasetType = DatasetType.ACS,
                 surveyType: SurveyType = SurveyType.ACS1,
                 shouldLoadFromExistingCache: bool = False):
        self.year = year
        self.datasetType = datasetType
        self.surveyType = surveyType

        self.groupCodes = _Codes()
        self.variableCodes = _Codes()

        self.__cache = VariableRetrievalCache(
            year=year,
            datasetType=datasetType,
            surveyType=surveyType,
            shouldLoadFromExistingCache=shouldLoadFromExistingCache)

    def getGroups(self) -> pd.DataFrame:
        if self.__cache.groups is not None:
            logging.info('retrieveing group data from cache')
            return self.__cache.groups

        groups = getGroups(self.year, self.datasetType, self.surveyType)
        self.__cache.persist('groups', groups)

        groupCodesList: List[Dict[str, str]] = groups[[
            'code', 'description']].to_dict('records')
        self.groupCodes.addCodes(
            **{
                code['code']: _Code(code['code'], code['description'])
                for code in groupCodesList
            })

        return groups

    def getGeography(self) -> pd.DataFrame:
        if self.__cache.geography is not None:
            logging.info('retrieving geography data from cache')
            return self.__cache.geography

        geography = getGeographies(
            self.year, self.datasetType, self.surveyType)

        self.__cache.persist('geography', geography)

        return geography

    def getVariablesByGroup(self, groups: List[str]) -> pd.DataFrame:
        allVars: pd.DataFrame = None

        notFoundGroups = set(groups)

        for group in groups:
            if group in self.__cache.variables:
                logging.info(f'retrieving variables for group {group}')

                notFoundGroups.remove(group)

                varsForGroup = self.__cache.variables[group]

                if allVars is None:
                    allVars = varsForGroup
                else:
                    allVars = allVars.append(varsForGroup, ignore_index=True)

        for group in notFoundGroups:
            varsForGroup = getVariables(
                group, self.year, self.datasetType, self.surveyType)

            self.__cache.persist(group, varsForGroup)

            variableCodesList: List[Dict[str, str]] = varsForGroup[[
                'code', 'name']].to_dict('records')
            self.variableCodes.addCodes(
                **{
                    code['code']: _Code(code['code'], code['name'])
                    for code in variableCodesList
                })

            if allVars is None:
                allVars = varsForGroup
            else:
                allVars = allVars.append(varsForGroup, ignore_index=True)

        return allVars

    def searchGroups(self, regex: str) -> pd.DataFrame:
        logging.info(f'searching groups for pattern {regex}')

        groups = self.getGroups()

        series: pd.Series = groups['description'].str.contains(
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

        series = variables[searchBy].str.contains(regex, case=False)

        return variables[series]

    def purgeCache(self, inMemory: bool = True, onDisk: bool = False) -> None:
        self.__cache.purge(inMemory, onDisk)

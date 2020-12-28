import pandas as pd
from models.SurveyType import SurveyType
from models.DatasetType import DatasetType
from api.variableGet.getVariableData import getVariableData
from dataFrames.variablesToDataframe import variablesToDataframe


def getVariables(group: str,
                 year: int,
                 datasetType: DatasetType = DatasetType.ACS,
                 surveyType: SurveyType = SurveyType.ACS1) -> pd.DataFrame:
    varData = getVariableData(group, year, datasetType, surveyType)
    return variablesToDataframe(varData)

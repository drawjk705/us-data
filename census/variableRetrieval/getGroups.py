from models import DatasetType, SurveyType
import pandas as pd
from api.variableGet.getGroups import getGroups as getGroupData
from dataFrames.groupDataToDataFrame import groupDataToDataFrame


def getGroups(year: int,
              datasetType: DatasetType = DatasetType.ACS,
              surveyType: SurveyType = SurveyType.ACS1) -> pd.DataFrame:
    groupRes = getGroupData(year, datasetType, surveyType)
    return groupDataToDataFrame(groupRes)

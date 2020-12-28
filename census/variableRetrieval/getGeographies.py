import pandas as pd
from dataFrames.geoDataToDataFame import geoDataToDataFrame
from api.variableGet import getSupportedGeographies
from models.SurveyType import SurveyType
from models.DatasetType import DatasetType


def getGeographies(year: int,
                   datasetType: DatasetType = DatasetType.ACS,
                   surveyType: SurveyType = SurveyType.ACS1) -> pd.DataFrame:
    geos = getSupportedGeographies(year, datasetType, surveyType)
    return geoDataToDataFrame(geos)

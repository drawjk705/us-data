from api.ApiConfig import ApiConfig
import pandas as pd
from dataFrames.geoDataToDataFame import geoDataToDataFrame
from api.variableGet.getSupportedGeographies import getSupportedGeographies


def getGeographies(apiConfig: ApiConfig) -> pd.DataFrame:
    geos = getSupportedGeographies(apiConfig)
    return geoDataToDataFrame(geos)

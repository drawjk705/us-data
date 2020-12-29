import pandas as pd
from api.ApiConfig import ApiConfig
from api.variableGet.fetchSupportedGeographiesData import \
    fetchSupportedGeographiesData
from dataFrames import geoDataToDataFrame


def getSupportedGeographies(apiConfig: ApiConfig) -> pd.DataFrame:
    geos = fetchSupportedGeographiesData(apiConfig)
    return geoDataToDataFrame(geos)

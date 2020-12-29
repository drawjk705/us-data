import pandas as pd
from api.variableGet.fetchGroupsData import fetchGroupData
from api.ApiConfig import ApiConfig
from dataFrames import groupDataToDataFrame


def getGroups(apiConfig: ApiConfig) -> pd.DataFrame:
    groupRes = fetchGroupData(apiConfig)
    return groupDataToDataFrame(groupRes)

import pandas as pd
from api.variableGet.getGroupsData import getGroupData
from api.ApiConfig import ApiConfig
from dataFrames.groupDataToDataFrame import groupDataToDataFrame


def getGroups(apiConfig: ApiConfig) -> pd.DataFrame:
    groupRes = getGroupData(apiConfig)
    return groupDataToDataFrame(groupRes)

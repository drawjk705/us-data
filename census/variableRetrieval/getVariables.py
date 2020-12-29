from api.ApiConfig import ApiConfig
import pandas as pd
from api.variableGet.fetchVariableData import fetchVariableData
from dataFrames import variablesToDataframe


def getVariables(group: str,
                 apiConfig: ApiConfig) -> pd.DataFrame:
    varData = fetchVariableData(group, apiConfig)
    return variablesToDataframe(varData)

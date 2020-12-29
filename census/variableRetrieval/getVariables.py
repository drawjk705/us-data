from api.ApiConfig import ApiConfig
import pandas as pd
from api.variableGet.getVariableData import getVariableData
from dataFrames.variablesToDataframe import variablesToDataframe


def getVariables(group: str,
                 apiConfig: ApiConfig) -> pd.DataFrame:
    varData = getVariableData(group, apiConfig)
    return variablesToDataframe(varData)

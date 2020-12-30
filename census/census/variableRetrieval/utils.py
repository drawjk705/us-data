from typing import List

import census.api.fetch as fetch
import census.dataTransformation.toDataFrame as toDataFrame
import pandas as pd
from census.api.ApiConfig import ApiConfig
from census.models import GeoDomain


def getGeographyCodes(
    apiConfig: ApiConfig, forDomain: GeoDomain, inDomains: List[GeoDomain]
) -> pd.DataFrame:
    codes = fetch.geographyCodes(apiConfig, forDomain, inDomains)
    return toDataFrame.geographyCodes(codes)


def getGroups(apiConfig: ApiConfig) -> pd.DataFrame:
    groupRes = fetch.groupData(apiConfig)
    return toDataFrame.groupData(groupRes)


def getSupportedGeographies(apiConfig: ApiConfig) -> pd.DataFrame:
    geos = fetch.supportedGeographies(apiConfig)
    return toDataFrame.supportedGeographies(geos)


def getVariables(group: str, apiConfig: ApiConfig) -> pd.DataFrame:
    varData = fetch.variableData(group, apiConfig)
    return toDataFrame.variables(varData)
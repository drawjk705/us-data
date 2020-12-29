from typing import List
from models import GeoDomain
from api import ApiConfig
import pandas as pd
from dataFrames import geographyCodesToDataFrame
from api.geographyCodesGet import fetchGeographyCodes


def getGeographyCodes(apiConfig: ApiConfig, forDomain: GeoDomain, inDomains: List[GeoDomain]) -> pd.DataFrame:
    codes = fetchGeographyCodes(apiConfig, forDomain, inDomains)
    return geographyCodesToDataFrame(codes)

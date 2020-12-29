from typing import List
from api.models import Domain
from api import ApiConfig
import pandas as pd
from dataFrames import geographyCodesToDataFrame
from api.geographyCodesGet import fetchGeographyCodes


def getGeographyCodes(apiConfig: ApiConfig, forDomain: Domain, inDomains: List[Domain]) -> pd.DataFrame:
    codes = fetchGeographyCodes(apiConfig, forDomain, inDomains)
    return geographyCodesToDataFrame(codes)

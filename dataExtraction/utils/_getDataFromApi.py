import requests
import pandas as pd
from typing import List, Tuple
import utils

MAX_FIELDS_IN_API_CALL = 50


def getDatafromApi(codesAndTitles: List[Tuple[str, str]]) -> pd.DataFrame:
    dfs: List[pd.DataFrame] = []
    allTitles = []

    for chunk in utils.chunk(codesAndTitles, MAX_FIELDS_IN_API_CALL):
        codes = [code for code, _ in chunk]
        titles = [title for _, title in chunk]
        allTitles += titles

        url = utils.buildUrl(','.join(codes))

        res: List[List] = requests.get(url).json()
        df = pd.DataFrame(res[1:], columns=res[0])
        df.columns = titles + ['stateCode', 'districtNum']
        dfs.append(df)

    mainDf = dfs[0]
    for df in dfs[1:]:
        mainDf = mainDf.drop(columns=['stateCode', 'districtNum'])
        mainDf = pd.concat([mainDf, df], axis=1, join='outer')
    mainDf.columns = allTitles + ['stateCode', 'districtNum']

    return mainDf

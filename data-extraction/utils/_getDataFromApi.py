import requests
import pandas as pd
from typing import List, Tuple
import utils


def getDatafromApi(codesAndTitles: List[Tuple[str, str]]) -> pd.DataFrame:
    codes = [code for code, _ in codesAndTitles]
    titles = [title for _, title in codesAndTitles]

    url = utils.buildUrl(','.join(codes))

    res = requests.get(url).json()

    df = pd.DataFrame(res)
    df.columns = titles + ['censusCode', 'district']
    df = df[1:]

    return df

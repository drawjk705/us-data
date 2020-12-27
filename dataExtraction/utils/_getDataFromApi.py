import requests
import pandas as pd
from typing import List, Tuple
import utils

# the API will throw if there are more than
# this number of fields requested in the
MAX_FIELDS_IN_API_CALL = 50


def getDatafromApi(codesAndTitles: List[Tuple[str, str]]) -> pd.DataFrame:
    """
    Pulls data from census API, and stores it in a pandas DataFrame

    Args:
        codesAndTitles (List[Tuple[str, str]]): list of tuples, with the codes (which the API
            needs to select particular fields) and a meaningful name for what each code
            actually represents

    Returns:
        pd.DataFrame: DataFrame with the data
    """

    dfs: List[pd.DataFrame] = []

    for chunk in utils.chunk(codesAndTitles, MAX_FIELDS_IN_API_CALL):
        codes = [code for code, _ in chunk]
        titles = [title for _, title in chunk]

        url = utils.buildUrl(','.join(codes))

        res: List[List] = requests.get(url).json()
        # The first entry in list of results are the column headers
        # i.e., the codes. So we set the columns to be the meaningful
        # field names which we derived
        columns = titles + ['stateCode', 'districtNum']
        df = pd.DataFrame(res[1:], columns=columns)
        dfs.append(df)

    # In the event that we need to make more than one call to the API,
    # we need to join all of the DataFrames
    mainDf = dfs[0]
    for df in dfs[1:]:
        # we drop these columns from the main DataFrame, since the
        # to-be-joined DataFrame will also have these columns
        mainDf = mainDf.drop(columns=['stateCode', 'districtNum'])
        mainDf = pd.concat([mainDf, df], axis=1, join='outer')

    return mainDf

from typing import List
import pandas as pd


def geographyCodesToDataFrame(geoCodes: List[List[str]]) -> pd.DataFrame:
    return pd.DataFrame(geoCodes[1:], columns=geoCodes[0])

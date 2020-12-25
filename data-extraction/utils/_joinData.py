import pandas as pd
import utils

columns_to_drop = ['censusCode', 'district', 'stateName', 'stateAbbr']


def joinData(newData: pd.DataFrame) -> pd.DataFrame:
    states = utils.loadDataFile('stateIds')

    states['censusCode'] = states['censusCode'].astype(str)
    states['district'] = states['district'].astype(str)

    newData['censusCode'] = newData['censusCode'].astype(str)
    newData['district'] = newData['district'].astype(str)

    df = pd.merge(newData, states, on=['censusCode', 'district'])
    df = df.drop(columns_to_drop, axis=1)

    return df

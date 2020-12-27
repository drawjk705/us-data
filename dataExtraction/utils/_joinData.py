import pandas as pd
import utils

columns_to_drop = ['stateCode', 'districtNum', 'stateName', 'stateAbbr']


def joinData(newData: pd.DataFrame) -> pd.DataFrame:
    states = utils.loadDataFile('dbo/stateIds')

    states['stateCode'] = states['stateCode'].astype(int)
    states['districtNum'] = states['districtNum'].astype(int)

    newData['stateCode'] = newData['stateCode'].astype(int)
    newData['districtNum'] = newData['districtNum'].astype(int)

    df = pd.merge(newData, states, on=['stateCode', 'districtNum'])
    df = df.drop(columns_to_drop, axis=1)

    return df

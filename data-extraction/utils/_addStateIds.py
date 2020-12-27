import pandas as pd
from constants import DATA_FILES_DIR

columns_to_drop = ['stateCode', 'districtNum', 'stateName', 'stateAbbr']


def addStateIds(newData: pd.DataFrame) -> pd.DataFrame:
    """
    Adds the state IDs (e.g, CA-01 -- [state]-[congressional district number])
    to the passed-in DataFrame

    Args:
        newData (pd.DataFrame): The state IDs will be added to this

    Returns:
        pd.DataFrame: The `newData` augmented with the state IDs
    """

    states = pd.read_csv(f'{DATA_FILES_DIR}/dbo/stateIds.csv')

    states['stateCode'] = states['stateCode'].astype(int)
    states['districtNum'] = states['districtNum'].astype(int)

    newData['stateCode'] = newData['stateCode'].astype(int)
    newData['districtNum'] = newData['districtNum'].astype(int)

    df = pd.merge(newData, states, on=['stateCode', 'districtNum'])
    df = df.drop(columns_to_drop, axis=1)

    return df

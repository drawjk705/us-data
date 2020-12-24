import pandas as pd

DIR = '~/src/us-stats/data-extraction/dataFiles'


def loadDataFile(file: str) -> pd.DataFrame:
    """
    loads file into datafame

    Args:
        file (str): the filename

    Returns:
        pd.DataFrame
    """

    filename = file if file.endswith('.csv') else f'{file}.csv'
    return pd.read_csv(f'{DIR}/{filename}')

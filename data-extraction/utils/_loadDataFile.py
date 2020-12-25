from constants import DATA_FILES_DIR
import pandas as pd


def loadDataFile(file: str) -> pd.DataFrame:
    filename = file if file.endswith('.csv') else f'{file}.csv'
    return pd.read_csv(f'{DATA_FILES_DIR}/{filename}')

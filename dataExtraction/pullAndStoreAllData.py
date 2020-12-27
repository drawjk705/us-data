import logging
from constants import DATA_FILES_DIR
from typing import Dict
from utils import getDatafromApi, joinData
import json
from pathlib import Path


def pullAndStoreAllData():
    logging.info('pulling and storing data')
    schemas: Dict[str, Dict[str, Dict[str, str]]] = {}
    with open('codesForDb.json', 'r') as f:
        schemas = json.load(f)

    for schema, tableDict in schemas.items():
        for tableName, codesDict in tableDict.items():
            logging.info(f'{schema}.{tableName}')
            codes = list(codesDict.keys())
            titles = list(codesDict.values())
            codesAndTitles = list(zip(codes, titles))

            apiData = getDatafromApi(codesAndTitles)

            df = joinData(apiData)

            path = Path(f'{DATA_FILES_DIR}/{schema}')
            path.mkdir(parents=True, exist_ok=True)

            df.to_csv(f'{path.absolute()}/{tableName}.csv', index=False)

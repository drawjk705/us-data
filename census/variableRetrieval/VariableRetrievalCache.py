import pandas as pd
from typing import Dict, Optional
import logging
from models import DatasetType, SurveyType
from pathlib import Path
import shutil

CACHE_DIR = 'cache'


class VariableRetrievalCache:
    groups: Optional[pd.DataFrame] = None
    geography: Optional[pd.DataFrame] = None
    variables: Dict[str, pd.DataFrame] = {}

    __inMemory: bool
    __onDisk: bool

    __year: int
    __datasetType: DatasetType
    __surveyType: SurveyType
    __shouldLoadFromExistingCache: bool

    __onDiskCacheDir: str

    def __init__(self,
                 year: int,
                 datasetType: DatasetType = DatasetType.ACS,
                 surveyType: SurveyType = SurveyType.ACS1,
                 inMemory: bool = True,
                 onDisk: bool = False,
                 shouldLoadFromExistingCache=False) -> None:

        if not inMemory and not onDisk:
            raise Exception('cache must be in-memory and/or on-disk')

        logMsg = 'creating '
        if inMemory:
            logMsg += 'in-memory '
        if onDisk:
            if inMemory:
                logMsg += 'and '
            logMsg += ' on-disk '
        logMsg += f'cache for {year} {datasetType.value} - {surveyType.value}'

        logging.info(logMsg)

        self.__inMemory = inMemory
        self.__onDisk = onDisk

        self.__year = year
        self.__datasetType = datasetType
        self.__surveyType = surveyType
        self.__shouldLoadFromExistingCache = shouldLoadFromExistingCache

        self.__onDiskCacheDir = f'{CACHE_DIR}/{year}/{datasetType.value}/{surveyType.value}'

        self.__setUpOnDickCache()

    def __setUpOnDickCache(self) -> None:
        if not self.__onDisk:
            return

        path = Path(self.__onDiskCacheDir)
        path.mkdir(parents=True, exist_ok=True)

        logging.info(
            f'creating cache directories, located at {path.absolute()}')

        if self.__shouldLoadFromExistingCache:
            logging.info('loading from existing on-disk cache...')

            for d in path.iterdir():
                if d.name != 'variables':
                    df = pd.read_csv(d.absolute())
                    dataName = d.with_suffix('').name
                    self.__dict__.update({dataName: df})
                else:
                    for varCsv in d.iterdir():
                        df = pd.read_csv(varCsv.absolute())
                        dataName = d.with_suffix('').name
                        self.variables.update({dataName, df})

    def persist(self, dataType: str, data: pd.DataFrame) -> None:
        self.__persistOnDisk(dataType, data)
        self.__persistInMemory(dataType, data)

    def __persistOnDisk(self, dataType: str, data: pd.DataFrame) -> None:
        if not self.__onDisk:
            return

        logging.info(f'persisting {dataType} on disk')

        path: Path = None

        if dataType not in ['groups', 'geography']:
            path = Path(f'{self.__onDiskCacheDir}/variables')

        else:
            path = Path(f'{self.__onDiskCacheDir}')

        path.mkdir(parents=True, exist_ok=True)

        data.to_csv(f'{path.absolute()}/{dataType}.csv')

    def __persistInMemory(self, dataType: str, data: pd.DataFrame) -> None:
        if not self.__inMemory:
            return

        logging.info(f'persisting {dataType} in memory')

        if dataType not in ['groups', 'geography']:
            self.variables.update({dataType: data})
        else:
            self.__dict__.update({dataType: data})

    def purge(self, inMemory: bool = True, onDisk: bool = False) -> None:
        if not inMemory and not onDisk:
            raise Exception('cache purges must be in-memory and/or on disk')

        logStr = 'purging cache '
        if inMemory:
            logStr += 'in memory'
        if onDisk:
            if inMemory:
                logStr += ' and '
            logStr += 'on disk'

        logging.info(logStr)

        if inMemory:
            self.groups = None
            self.geography = None
            self.variables = {}
        if onDisk:
            shutil.rmtree(CACHE_DIR)

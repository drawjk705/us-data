import shutil
import logging
from buildSchema import buildSchema
from constants import DATA_FILES_DIR
from buildStateIds import buildStateIds
from pullAndStoreAllData import pullAndStoreAllData
from utils import configureLogger
from buildSqlScripts import buildSqlScripts
from createDbAndTables import createDbAndTables

logFile = 'data-extraction.log'

configureLogger(logFile)

try:
    logging.info(f'removing {DATA_FILES_DIR}...')
    shutil.rmtree(DATA_FILES_DIR)
except:
    logging.info(f'no need to remove {DATA_FILES_DIR}')

buildSchema()
buildStateIds()
pullAndStoreAllData()
buildSqlScripts()
createDbAndTables()

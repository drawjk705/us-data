import shutil
import logging
from generateSqlScripts import generateSqlScripts
from buildSchema import buildSchema
from constants import DATA_FILES_DIR
from stateIds import buildStateIds
from pullAndStoreAllData import pullAndStoreAllData
from utils import configureLogger
from _buildSqlScripts import buildSqlScripts

configureLogger('data-extraction.log')

try:
    logging.info(f'removing {DATA_FILES_DIR}...')
    shutil.rmtree(DATA_FILES_DIR)
except:
    logging.info(f'no need to remove {DATA_FILES_DIR}')

buildSchema()
buildStateIds()
pullAndStoreAllData()
buildSqlScripts()

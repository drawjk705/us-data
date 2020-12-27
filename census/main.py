import collections
from dataFrames import geoDataToDataFrame
from api import getSupportedGeographies
import json
from pprint import pprint
from utils import configureLogger
import pandas as pd

configureLogger('census.log')

supportedGeos = getSupportedGeographies(2019)

geoDataToDataFrame(supportedGeos).to_csv('test.csv')

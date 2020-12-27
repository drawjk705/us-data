import logging
import requests
from api import getSupportedGeographies
from pprint import pprint
from utils import configureLogger

configureLogger('census.log')

supportedGeos = getSupportedGeographies(2019)

pprint(supportedGeos)

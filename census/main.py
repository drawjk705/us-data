from models.GeoDomain import GeoDomain
from utils.configureLogger import configureLogger
from variableRetrieval.VariableRetriever import VariableRetriever


configureLogger('census.log')

c = VariableRetriever(2019, shouldLoadFromExistingCache=True)
supportedGeos = c.getSupportedGeographies()

c.getGeographyCodes(forDomain=GeoDomain('county', '*'),
                    inDomains=[GeoDomain("state", "01")])
c.getGeographyCodes(forDomain=GeoDomain('county', '*'),
                    inDomains=[GeoDomain("state", "01"), GeoDomain("us", "*")])
c.getGeographyCodes(forDomain=GeoDomain('county', '*'),
                    inDomains=[GeoDomain("state", "01")])

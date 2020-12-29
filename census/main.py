from utils.configureLogger import configureLogger
from api.models.Domain import Domain
from variableRetrieval.VariableRetriever import VariableRetriever


configureLogger('census.log')

c = VariableRetriever(2019, shouldLoadFromExistingCache=True)
supportedGeos = c.getSupportedGeographies()

c.getGroups()

geoCodes = c.getGeographyCodes(Domain('us', '*'))
geoCodes = c.getGeographyCodes(Domain('us', '*'))

c.getVariablesByGroup(['B17015'])

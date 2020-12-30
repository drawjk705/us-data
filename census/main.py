from census.models import GeoDomain
from census.utils.configureLogger import configureLogger
from census.variableRetrieval.variableRetriever import VariableRetriever


configureLogger("census.log")

c = VariableRetriever(2019, shouldLoadFromExistingCache=True)
supportedGeos = c.getSupportedGeographies()

c.getGeographyCodes(
    forDomain=GeoDomain("county"), inDomains=[GeoDomain("state", "01"), GeoDomain("us")]
)

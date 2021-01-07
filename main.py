from census.models import GeoDomain
from census.getCensus import getCensus

c = getCensus(2019, shouldReplaceColumnHeaders=True)

c.getGroups()
geoDomains = [GeoDomain("congressional district"), GeoDomain("state")]

blackPovVars = c.getVariablesByGroup(
    c.groups.PovertyStatusInThePast12MonthsByAgeBlackOrAfricanAmericanAlone.code
)

blackPovStats = c.getStats(blackPovVars["code"].tolist(), *geoDomains)

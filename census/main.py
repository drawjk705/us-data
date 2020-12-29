from variableRetrieval.VariableRetriever import VariableRetriever
from utils.configureLogger import configureLogger

configureLogger('census.log')

c = VariableRetriever(2019, shouldLoadFromExistingCache=True)

c.getGeography()
searchedGroups = c.searchGroups('family')
variables = c.getVariablesByGroup(groups=['B19202H'])
searchedVars = c.searchVariables(
    r'margin', inGroups=['B19202H'], searchBy='name')

print(searchedVars)

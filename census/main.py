from variableRetrieval.VariableRetriever import VariableRetriever
from utils import configureLogger

configureLogger('census.log')

c = VariableRetriever(2019, onDiskCache=True)

searchedGroups = c.searchGroups('family')
variables = c.getVariablesByGroup(groups=['B19202H'])
searchedVars = c.searchVariables(
    r'margin', inGroups=['B19202H'], searchBy='name')

print(searchedVars)

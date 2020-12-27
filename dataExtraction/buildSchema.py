from collections import OrderedDict
import json
import logging
from os import replace
import re
import requests
from typing import Dict, Generator, List, Tuple
from constants import CENSUS_TOPICS_URL, schemasToTables

concepts = [concept
            for table in schemasToTables.values()
            for concept in table.values()]

MAX_SQL_COL_LEN = 128


def __getVariableUrlWithGroup() -> Generator[Tuple[str, str], None, None]:
    groups: Dict[str, List[Dict[str, str]]] = requests.get(
        CENSUS_TOPICS_URL).json()

    groupsByConcept = {group['description']: {'name': group['name'], 'vars': group['variables']}
                       for group in groups['groups']}

    for concept in concepts:
        # we want to exclude C-prefixed groups since those care comparisons
        if concept in groupsByConcept and groupsByConcept[concept]['name'].startswith('B'):
            url = groupsByConcept[concept]['vars']
            yield url, concept


def toCamelCase(string: str) -> str:
    uppercasedList = [
        f'{token[0].upper()}{token[1:]}' for token in re.sub(r'\(\)', '', string).split(' ')]
    return ''.join(uppercasedList)


def __makeVariableName(variable: str) -> str:
    prefix = 'Estimate!!Total:!!'
    delimiter = ':!!'

    if not variable.startswith(prefix) or variable.endswith(':'):
        return ''

    camelCasedVar = toCamelCase(variable)

    newName = camelCasedVar.replace(prefix, '') \
        .replace(delimiter, '_') \
        .replace('!!', '_') \
        .replace("'", '')

    stringsToRemove = ['InThePast12Months',
                       'FiberOpticOrDSL_']

    # this is to ensure that the new name has fewer than 128 characters
    for stringToRemove in stringsToRemove:
        if stringToRemove in newName:
            newName = newName.replace(stringToRemove, '')

    newName = re.sub(r"[,-]", ' ', newName).replace(' ', '_')
    newName = re.sub(r'\$', 'USD_', newName)

    if len(newName) >= MAX_SQL_COL_LEN:
        logging.error(
            f'column {newName} has length greater than max SQL column length of {MAX_SQL_COL_LEN}')

    return newName


def __getVariablesFromUrl(url: str) -> Dict[str, str]:
    variables: Dict[str, Dict[str, Dict[str, str]]] = requests.get(url).json()

    variablesToReturn: Dict[str, str] = {}

    for varCode, contents in variables['variables'].items():
        varName = __makeVariableName(contents['label'])
        if not len(varName):
            continue

        variablesToReturn[varCode] = varName

    return variablesToReturn


schemaInverted: Dict[str, Tuple[str, str]] = {}
for schema, tableDict in schemasToTables.items():
    for tableName, concept in tableDict.items():
        schemaInverted[concept] = (schema, tableName)


def __associateVariablesWithTables():
    schemaToTableToVariables: Dict[str, Dict[str, OrderedDict[str, str]]] = {}

    for url, group in __getVariableUrlWithGroup():
        variables = __getVariablesFromUrl(url)
        path = schemaInverted[group]
        if path[0] not in schemaToTableToVariables:
            schemaToTableToVariables[path[0]] = {}

        schemaToTableToVariables[path[0]][path[1]
                                          ] = OrderedDict(sorted(variables.items()))

    return schemaToTableToVariables


def buildSchema():
    logging.info('building schema...')
    schema = __associateVariablesWithTables()
    with open('codesForDb.json', 'w') as f:
        json.dump(schema, f)
    logging.info('schema built')

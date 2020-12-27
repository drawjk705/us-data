"""buildSchema

    Background
    -----------

    The US Census API has quantitative data on a whole range of items, each of
    which is subsumed under a category, or in the API's terms, a "concept" or "group".

    The /groups.json endpoint maps each group to an endpoint which lists 
    all of that group's variables (i.e., the data points it has). Each of
    these variables has a code name for querying the census API e.g., B0012_001,
    as well as its semantic meaning, which looks something like this: `Estimate!!Total:!!Male:!!5 to 9 years`

    Purpose:
    ---------    
    This module provides the code to do the following:
        1. Get all concepts from the API that we're interested in (determined by `schemasToTables`)
        2. Get all variables for each concept of interest
        3. Filter out variables we aren't interested in
        4. Store the result in JSON file we'll access later, whose format will look something like this:
        
            {
                "sqlSchemaName": {
                    "sqlTableName": {
                        "VARIABLE_CODE_FOR_API": "variableMeaningAndColumnNameForSql"
                    }
                }
            }
"""
from collections import OrderedDict
import json
import logging
import re
import requests
from typing import Dict, Generator, List, Tuple
from constants import CENSUS_TOPICS_URL, schemasToTables

concepts = [concept
            for table in schemasToTables.values()
            for concept in table.values()]

MAX_SQL_COL_LEN = 128


def __getVariableUrlWithGroup() -> Generator[Tuple[str, str], None, None]:
    """
    Generator which will yield the URL to find the variables for a given topic,
    along with the associated topic

    Yields:
        Generator[Tuple[str, str], None, None]: Each tuple returned from the generator will
        be of the following signature: `(url, groupTopic)`
    """

    groups: Dict[str, List[Dict[str, str]]] = requests.get(
        CENSUS_TOPICS_URL).json()

    # restructuring the above result, so we can index by the group's concept
    groupsByConcept = {
        group['description']:
        {
            'name': group['name'],
            'vars': group['variables']
        }
        for group in groups['groups']
    }

    for concept in concepts:
        # we want to exclude C-prefixed groups since those are comparisons
        if concept in groupsByConcept and groupsByConcept[concept]['name'].startswith('B'):
            url = groupsByConcept[concept]['vars']
            yield url, concept


def toCamelCase(string: str) -> str:
    """
    utility function to camelCase-ify a string

    Args:
        string (str)

    Returns:
        str: in camel case
    """

    uppercasedList = [
        f'{token[0].upper()}{token[1:]}'
        for token in re.sub(r'\(\)', '', string).split(' ')
    ]
    return ''.join(uppercasedList)


def __makeVariableName(variable: str) -> Tuple[str, bool]:
    """
    builds the name for the very long census data variable name

    Args:
        variable (str): the very long census data variable name

    Returns:
        Tuple[str, bool]: a more readable version of the variable name,
            along with whether or not to use this variable name. (We don't
            want to use ineligible variables. See below for more info on that.)
    """

    prefix = 'Estimate!!Total:!!'
    delimiter = ':!!'

    # The first condition will exclude any margin-of-error or annotation variables.
    # The second will exclude variables that have additional sub-fields, and are aggregates
    # of those sub-fields. (We can derive those aggregates on our own.)
    if not variable.startswith(prefix) or variable.endswith(':'):
        return '', False

    camelCasedVar = toCamelCase(variable)

    newName = camelCasedVar.replace(prefix, '') \
        .replace(delimiter, '_') \
        .replace('!!', '_') \
        .replace("'", '')

    # This is to ensure that the new name has fewer than 128 characters.
    # Not sure if there is a more elegant way to do this. Right now, this was
    # done by finding the offending variable names, and what could be chopped out
    stringsToRemove = ['InThePast12Months',
                       'FiberOpticOrDSL_']

    for stringToRemove in stringsToRemove:
        if stringToRemove in newName:
            newName = newName.replace(stringToRemove, '')

    newName = re.sub(r"[,-]", ' ', newName).replace(' ', '_')
    newName = re.sub(r'\$', 'USD_', newName)

    if len(newName) >= MAX_SQL_COL_LEN:
        logging.error(
            f'column {newName} has length greater than max SQL column length of {MAX_SQL_COL_LEN}')

    return newName, True


def __getVariablesFromUrl(url: str) -> Dict[str, str]:
    """
    Hits the API's URL with the list of variables for a given census topic,
    extracst the relevant variables, and gives them more intelligible names

    Args:
        url (str)

    Returns:
        Dict[str, str]: mapping of the variable's code to its semantic value
    """
    variables: Dict[str, Dict[str, Dict[str, str]]] = requests.get(url).json()

    variablesToReturn: Dict[str, str] = {}

    for varCode, contents in variables['variables'].items():
        varName, shouldUseVariable = __makeVariableName(contents['label'])
        if not shouldUseVariable:
            continue

        variablesToReturn[varCode] = varName

    return variablesToReturn


# an inverted version of the semantic "schema", which
# maps the API concepts to their schema and
# table name
schemaInverted: Dict[str, Tuple[str, str]] = {}
for schema, tableDict in schemasToTables.items():
    for tableName, concept in tableDict.items():
        schemaInverted[concept] = (schema, tableName)


def __associateVariablesWithTables() -> Dict[str, Dict[str, OrderedDict[str, str]]]:
    """
    Creates a mapping between the SQL schema, its table names,
    and the API variables/semantic meaning of those variables
    that will be associated with the respective table

    Returns:
        Dict[str, Dict[str, OrderedDict[str, str]]]: Mapping similar to the following:

        {
            "sqlSchemaName": {
                "sqlTableName": {
                    "VARIABLE_CODE_FOR_API": "variableMeaningAndColumnNameForSql"
                }
            }
        }
    """

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
    """
    Builds a rough schema: mapping SQL schemas to their tables,
    and mapping each table to its API variables, each of which is mapped
    to its semantic meaning (and ultimate SQL column name).
    Dumps this result in a JSON file
    """

    logging.info('building schema...')
    schema = __associateVariablesWithTables()
    with open('codesForDb.json', 'w') as f:
        json.dump(schema, f)
    logging.info('schema built')

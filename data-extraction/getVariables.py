from collections import OrderedDict
import json
import re
from pprint import pprint
import requests
from typing import Dict, Generator, List, Tuple

# https://api.census.gov/data/2019/acs/acs1/groups.html
schemaToTable: Dict[str, Dict[str, str]] = {
    'healthInsurance': {
        'whiteOnlyCoverage': 'HEALTH INSURANCE COVERAGE STATUS BY AGE (WHITE ALONE)',
        'blackCoverage': 'HEALTH INSURANCE COVERAGE STATUS BY AGE (BLACK OR AFRICAN AMERICAN ALONE)',
        'usIndianAndAlaskaNativeCoverage': 'HEALTH INSURANCE COVERAGE STATUS BY AGE (AMERICAN INDIAN AND ALASKA NATIVE ALONE',
        'asianCoverage': 'HEALTH INSURANCE COVERAGE STATUS BY AGE (ASIAN ALONE)',
        'hawaiianNativeCoverage': 'HEALTH INSURANCE COVERAGE STATUS BY AGE (NATIVE HAWAIIAN AND OTHER PACIFIC ISLANDER ALONE)',
        'otherRaceCoverage': 'HEALTH INSURANCE COVERAGE STATUS BY AGE (SOME OTHER RACE ALONE)',
        'biracialCoverage': 'HEALTH INSURANCE COVERAGE STATUS BY AGE (TWO OR MORE RACES)',
        'whiteNoLatinoCoverage': 'HEALTH INSURANCE COVERAGE STATUS BY AGE (WHITE ALONE, NOT HISPANIC OR LATINO)',
        'latinoHispanicCoverage': 'HEALTH INSURANCE COVERAGE STATUS BY AGE (HISPANIC OR LATINO)'
    },
    'education': {
        'educationalAttainment': 'CITIZEN, VOTING-AGE POPULATION BY EDUCATIONAL ATTAINMENT',
        'individualPovertyStatusByEducation': 'POVERTY STATUS IN THE PAST 12 MONTHS OF INDIVIDUALS BY SEX BY EDUCATIONAL ATTAINMENT',
        'familyPovertyStatusByHouseholderEducation': 'POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY HOUSEHOLD TYPE BY EDUCATIONAL ATTAINMENT OF HOUSEHOLDER',
        'earningsBySexByEducation': 'MEDIAN EARNINGS IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS) BY SEX BY EDUCATIONAL ATTAINMENT FOR THE POPULATION 25 YEARS AND OVER',
        'homeOwnershipByEducation': 'TENURE BY EDUCATIONAL ATTAINMENT OF HOUSEHOLDER',
        'insuranceCoverageByEducation': 'HEALTH INSURANCE COVERAGE STATUS AND TYPE BY AGE BY EDUCATIONAL ATTAINMENT'
    },
    'economics': {
        'povertyStatus': 'CITIZEN, VOTING-AGE POPULATION BY POVERTY STATUS',
        'employmentStatusByEducation': 'EDUCATIONAL ATTAINMENT BY EMPLOYMENT STATUS FOR THE POPULATION 25 TO 64 YEARS'
    },
    'resources': {
        'internetAccess': 'PRESENCE AND TYPES OF INTERNET SUBSCRIPTIONS IN HOUSEHOLD',
        'educationByTechAccess': 'EDUCATIONAL ATTAINMENT BY PRESENCE OF A COMPUTER AND TYPES OF INTERNET SUBSCRIPTION IN HOUSEHOLD',
        'laborForceStatusByTechAccess': 'LABOR FORCE STATUS BY PRESENCE OF A COMPUTER AND TYPES OF INTERNET SUBSCRIPTION IN HOUSEHOLD',
    }
}


concepts = [concept
            for table in schemaToTable.values()
            for concept in table.values()]


def getVariableUrlWithGroup() -> Generator[Tuple[str, str], None, None]:
    groups: Dict[str, List[Dict[str, str]]] = requests.get(
        'https://api.census.gov/data/2019/acs/acs1/groups.json').json()

    for group in groups['groups']:
        # we want to exclude C-prefixed groups since those care comparisons
        if group['description'] in concepts and group['name'].startswith('B'):
            url = group['variables']
            yield url, group['description']


def __buildVarName(nameComponents: List[str]) -> str:
    nameStr = []

    for component in nameComponents:
        componentModified = component.replace('!!', '_')
        uppercased = ''.join([token.capitalize()
                              for token in re.sub(r"[\(\),-]", ' ', componentModified).replace("'", '') .split(' ')])

        nameStr.append(uppercased)

    return '_'.join(nameStr)


def __getVariableToExtract(variable: str) -> str:
    prefix = 'Estimate!!Total:!!'
    delimiter = ':!!'

    if not variable.startswith(prefix) or variable.endswith(':'):
        return None

    return variable.removeprefix(prefix).split(delimiter)


def getVariablesFromUrl(url: str) -> Dict[str, str]:
    variables: Dict[str, Dict[str, str]] = requests.get(url).json()

    variablesToReturn: Dict[str, str] = {}

    for varCode, contents in variables['variables'].items():
        varToExtract = __getVariableToExtract(contents['label'])
        if varToExtract is None:
            continue

        varName = __buildVarName(varToExtract)

        variablesToReturn[varCode] = varName

    return variablesToReturn


schemaInverted: Dict[str, Tuple[str, str]] = {}
for schema, tableDict in schemaToTable.items():
    for tableName, concept in tableDict.items():
        schemaInverted[concept] = (schema, tableName)


def associateVariablesWithTables():
    schemaToTableToVariables = {}

    for url, group in getVariableUrlWithGroup():
        variables = getVariablesFromUrl(url)
        path = schemaInverted[group]
        if path[0] not in schemaToTableToVariables:
            schemaToTableToVariables[path[0]] = {}
        schemaToTableToVariables[path[0]][path[1]
                                          ] = OrderedDict(sorted(variables.items()))

    return schemaToTableToVariables


schema = associateVariablesWithTables()
with open('codesForDb.json', 'w') as f:
    json.dump(schema, f)

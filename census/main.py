import logging
import requests
from api import getSupportedGeographies
from api.supportedVariableExtraction.getSupportedGeographies import __parseSupportedGeographies
from pprint import pprint
from utils import configureLogger

configureLogger('census.log')

test = {
    "default": [
        {
            "isDefault": "true"
        }
    ],
    "fips": [
        {
            "name": "us",
            "geoLevelDisplay": "010",
            "referenceDate": "2019-01-01"
        },
        {
            "name": "region",
            "geoLevelDisplay": "020",
            "referenceDate": "2019-01-01"
        },
        {
            "name": "division",
            "geoLevelDisplay": "030",
            "referenceDate": "2019-01-01"
        },
        {
            "name": "state",
            "geoLevelDisplay": "040",
            "referenceDate": "2019-01-01"
        },
        {
            "name": "county",
            "geoLevelDisplay": "050",
            "referenceDate": "2019-01-01",
            "requires": [
                "state"
            ],
            "wildcard": [
                "state"
            ],
            "optionalWithWCFor": "state"
        },
        {
            "name": "county subdivision",
            "geoLevelDisplay": "060",
            "referenceDate": "2019-01-01",
            "requires": [
                "state",
                "county"
            ],
            "wildcard": [
                "county"
            ],
            "optionalWithWCFor": "county"
        },
        {
            "name": "place",
            "geoLevelDisplay": "160",
            "referenceDate": "2019-01-01",
            "requires": [
                "state"
            ],
            "wildcard": [
                "state"
            ],
            "optionalWithWCFor": "state"
        },
        {
            "name": "alaska native regional corporation",
            "geoLevelDisplay": "230",
            "referenceDate": "2019-01-01",
            "requires": [
                "state"
            ],
            "wildcard": [
                "state"
            ],
            "optionalWithWCFor": "state"
        },
        {
            "name": "american indian area/alaska native area/hawaiian home land",
            "geoLevelDisplay": "250",
            "referenceDate": "2019-01-01"
        },
        {
            "name": "metropolitan statistical area/micropolitan statistical area",
            "geoLevelDisplay": "310",
            "referenceDate": "2019-01-01"
        },
        {
            "name": "principal city (or part)",
            "geoLevelDisplay": "312",
            "referenceDate": "2019-01-01",
            "requires": [
                "metropolitan statistical area/micropolitan statistical area",
                "state (or part)"
            ]
        },
        {
            "name": "metropolitan division",
            "geoLevelDisplay": "314",
            "referenceDate": "2019-01-01",
            "requires": [
                "metropolitan statistical area/micropolitan statistical area"
            ]
        },
        {
            "name": "combined statistical area",
            "geoLevelDisplay": "330",
            "referenceDate": "2019-01-01"
        },
        {
            "name": "combined new england city and town area",
            "geoLevelDisplay": "335",
            "referenceDate": "2019-01-01"
        },
        {
            "name": "new england city and town area",
            "geoLevelDisplay": "350",
            "referenceDate": "2019-01-01"
        },
        {
            "name": "principal city",
            "geoLevelDisplay": "352",
            "referenceDate": "2019-01-01",
            "requires": [
                "new england city and town area",
                "state (or part)"
            ],
            "wildcard": [
                "state (or part)"
            ],
            "optionalWithWCFor": "state (or part)"
        },
        {
            "name": "necta division",
            "geoLevelDisplay": "355",
            "referenceDate": "2019-01-01",
            "requires": [
                "new england city and town area"
            ]
        },
        {
            "name": "urban area",
            "geoLevelDisplay": "400",
            "referenceDate": "2019-01-01"
        },
        {
            "name": "congressional district",
            "geoLevelDisplay": "500",
            "referenceDate": "2019-01-01",
            "requires": [
                "state"
            ],
            "wildcard": [
                "state"
            ],
            "optionalWithWCFor": "state"
        },
        {
            "name": "public use microdata area",
            "geoLevelDisplay": "795",
            "referenceDate": "2019-01-01",
            "requires": [
                "state"
            ],
            "wildcard": [
                "state"
            ],
            "optionalWithWCFor": "state"
        },
        {
            "name": "school district (elementary)",
            "geoLevelDisplay": "950",
            "referenceDate": "2019-01-01",
            "requires": [
                "state"
            ]
        },
        {
            "name": "school district (secondary)",
            "geoLevelDisplay": "960",
            "referenceDate": "2019-01-01",
            "requires": [
                "state"
            ]
        },
        {
            "name": "school district (unified)",
            "geoLevelDisplay": "970",
            "referenceDate": "2019-01-01",
            "requires": [
                "state"
            ]
        }
    ]
}


gs = __parseSupportedGeographies(test)

logging.info('yp')

for k, g_set in gs.items():
    print(k)
    print('--------------')
    for g in g_set:
        print(g)

        inClause = '' if not len(
            g.inClauses) else '&in=' + '&in='.join(g.inClauses)
        inClause = inClause.replace('CODE', '02')
        forClause = '&for=' + g.forClause.replace('CODE', '01')
        url = f'https://api.census.gov/data/2019/acs/acs1?get=NAME{forClause}{inClause}'
        print(url)
        res = requests.get(url)

        if res.status_code == 200:
            print(res.json())

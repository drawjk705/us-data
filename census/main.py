from api import getSupportedGeographies
from api.supportedVariableExtraction.getSupportedGeographies import __parseSupportedGeographies

test = {
    "default": {},
    "fips": [{
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
        "optionalWithWCFor": "county"}]
}


__parseSupportedGeographies(test)

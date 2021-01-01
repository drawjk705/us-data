from census.api.models import GroupVariable
from census.dataTransformation.toDataFrame import DataFrameTransformer


res = [
    ["NAME", "B01001_001E", "B01001_002E", "B01001_003E", "state", "county"],
    ["Sedgwick County, Kansas", "516042", "254525", "17590", "20", "173"],
    ["Douglas County, Kansas", "122259", "59682", "3095", "20", "045"],
    ["Shawnee County, Kansas", "176875", "85685", "5244", "20", "177"],
    ["Johnson County, Kansas", "602401", "295214", "18934", "20", "091"],
    ["Wyandotte County, Kansas", "165429", "81928", "6716", "20", "209"],
    ["Butler County, Kansas", "66911", "33786", "2355", "20", "015"],
    ["Leavenworth County, Kansas", "81758", "43759", "2581", "20", "103"],
    ["Riley County, Kansas", "74232", "39233", "1546", "20", "161"],
]

varJson = {
    "B01001_001E": {
        "label": "Estimate!!Total:",
        "concept": "SEX BY AGE",
        "predicateType": "string",
        "group": "B01001",
        "limit": 0,
        "predicateOnly": True,
    },
    "B01001_002E": {
        "label": "Estimate!!Total:!!Male:",
        "concept": "SEX BY AGE",
        "predicateType": "int",
        "group": "B01001",
        "limit": 0,
        "predicateOnly": True,
    },
    "B01001_003E": {
        "label": "Estimate!!Total:!!Male:!!Under 5 years",
        "concept": "SEX BY AGE",
        "predicateType": "int",
        "group": "B01001",
        "limit": 0,
        "predicateOnly": True,
    },
}

groupVars = [GroupVariable.fromJson(key, value) for key, value in varJson.items()]

t = DataFrameTransformer()

df = t.stats(res, groupVars)

print(df)
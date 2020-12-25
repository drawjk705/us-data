import re
import requests
from typing import Dict
from pprint import pprint
import pandas as pd
from models.State import State
from utils import buildUrl
from constants import stateAbbreviations


def extractState(data: list) -> str:
    name = data[0]
    return re.search(r', (.*)', name).group(1)


def getStatesAndDistricts() -> Dict[str, State]:
    url = buildUrl('NAME')
    res = requests.get(url).json()

    states: Dict[str, State] = {}

    for line in res[1:]:
        name = extractState(line)

        if line[1] in states:
            state = states[line[1]]
            state.addDistrict(line[2])
        else:
            states[line[1]] = State(name)
            states[line[1]].addDistrict(line[2])

    pprint(states)

    statesList = []
    for code, state in states.items():
        for district in state.districts:
            stateAbbr = stateAbbreviations[state.name.upper()]

            obj = {
                'censusCode': code,
                'stateName': state.name,
                'stateAbbr': stateAbbr,
                'district': district,
                'stateId': f'{stateAbbr}-{district}'
            }
            statesList.append(obj)

    return statesList


states = getStatesAndDistricts()
print(states)
df = pd.DataFrame(states).sort_values(
    ['stateName', 'district'], ascending=[True, True])

print(df.head())
df.to_csv('dataFiles/stateIds.csv', index=False)

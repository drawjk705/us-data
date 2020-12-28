import pandas as pd
from typing import Dict
from api.models.Group import Group


def groupDataToDataFrame(groupData: Dict[str, Group]) -> pd.DataFrame:
    groupsList = []
    for code, groupObj in groupData.items():
        groupDict = {
            'code': code,
            'description': groupObj.description
        }
        groupsList.append(groupDict)

    return pd.DataFrame(groupsList)

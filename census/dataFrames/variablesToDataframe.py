from typing import Dict, List
import pandas as pd
from api.models import GroupVariable


def variablesToDataframe(variables: List[GroupVariable]) -> pd.DataFrame:
    variableDictList: List[Dict] = []

    for variable in variables:
        variableDictList.append({
            "code": variable.code,
            "groupCode": variable.groupCode,
            "concept": variable.groupConcept,
            "name": variable.name,
            "limit": variable.limit,
            "predicateOnly": variable.predicateOnly,
            "predicateType": variable.predicateType
        })

    return pd.DataFrame(variableDictList)

from typing import List
import pandas as pd
from api.models.GroupVariable import GroupVariable


def variablesToDataframe(variables: List[GroupVariable]) -> pd.DataFrame:
    variableDictList: list[dict[str, str]] = []

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

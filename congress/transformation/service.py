import us
import pandas as pd
from congress.api.models import Congressman
from typing import Any, Dict, List
from congress.transformation.interface import ICongressTransformationService


class CongressTransformationService(ICongressTransformationService):
    def congressmembers(self, members: List[Congressman]) -> pd.DataFrame:
        membersFlat: List[Dict[str, Any]] = []

        for member in members:
            memberDict = {}
            for k, v in member.__dict__.items():
                if hasattr(v, "__dict__"):
                    for k1, v1 in v.__dict__.items():
                        key = f"{k}_{k1}"
                        memberDict.update({key: v1})
                else:
                    memberDict.update({k: v})
                memberDict.update(
                    {"fips": us.states.mapping("abbr", "fips")[member.state]}  # type: ignore
                )
                if "district" in memberDict:
                    memberDict.update({"district": memberDict["district"].zfill(2)})
            membersFlat.append(memberDict)

        sortKeys = ["fips"] + (["district"] if "district" in membersFlat[0] else [])

        return pd.DataFrame(membersFlat).sort_values(by=sortKeys)

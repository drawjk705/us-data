from dataclasses import dataclass
from enum import Enum


class DatasetType(str, Enum):
    ACS = "acs"


class SurveyType(str, Enum):
    ACS1 = "acs1"
    ACS5 = "acs5"


@dataclass
class GeoDomain:
    name: str
    codeOrWildcard: str

    def __init__(self, name: str, codeOrWildcard: str = "*") -> None:
        self.name = name
        self.codeOrWildcard = codeOrWildcard

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.name}:{self.codeOrWildcard}"

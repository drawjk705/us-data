from dataclasses import dataclass, field
from enum import Enum


class DatasetType(str, Enum):
    ACS = "acs"


class SurveyType(str, Enum):
    ACS1 = "acs1"
    ACS5 = "acs5"


@dataclass(frozen=True)
class GeoDomain:
    name: str
    codeOrWildcard: str = field(default="*")

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.name}:{self.codeOrWildcard}"

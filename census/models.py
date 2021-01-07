from dataclasses import dataclass, field
from enum import Enum


class DatasetType(str, Enum):
    ACS = "acs"
    DECENNIAL_CENSUS = "dec"


class SurveyType(str, Enum):
    ACS1 = "acs1"
    ACS5 = "acs5"
    SUMMARY_FILE_1 = "sf1"


@dataclass(frozen=True)
class GeoDomain:
    name: str
    codeOrWildcard: str = field(default="*")

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.name}:{self.codeOrWildcard}"

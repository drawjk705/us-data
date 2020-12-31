from dataclasses import dataclass
from census.models import SurveyType, DatasetType


@dataclass(frozen=True)
class Config:
    """

    Stores basic information for hitting the API,
    so that we don't need to pass the same variables
    around all of the time:
     - Survey year
     - Dataset type
     - Survey type
    """

    year: int = 2020
    datasetType: DatasetType = DatasetType.ACS
    surveyType: SurveyType = SurveyType.ACS1

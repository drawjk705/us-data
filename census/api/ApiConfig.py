from models.DatasetType import DatasetType
from models.SurveyType import SurveyType


class ApiConfig:
    year: int
    datasetType: DatasetType
    surveyType: SurveyType

    def __init__(self,
                 year: int,
                 datasetType: DatasetType = DatasetType.ACS,
                 surveyType: SurveyType = SurveyType.ACS1) -> None:
        self.year = year
        self.datasetType = datasetType
        self.surveyType = surveyType

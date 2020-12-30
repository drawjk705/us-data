from census.models import SurveyType, DatasetType


class ApiConfig:
    """ApiConfig

    Stores basic information for hitting the API,
    so that we don't need to pass the same variables
    around all of the time:
     - Survey year
     - Dataset type
     - Survey type
    """

    year: int
    datasetType: DatasetType
    surveyType: SurveyType

    def __init__(
        self,
        year: int,
        datasetType: DatasetType = DatasetType.ACS,
        surveyType: SurveyType = SurveyType.ACS1,
    ) -> None:
        self.year = year
        self.datasetType = datasetType
        self.surveyType = surveyType

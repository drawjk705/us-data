from models.DatasetType import DatasetType
from api.constants import API_URL_FORMAT
from models import SurveyType
import requests
from typing import Any


def getData_Base(year: int,
                 route: str = '',
                 datasetType: DatasetType = DatasetType.ACS,
                 surveyType: SurveyType = SurveyType.ACS1) -> Any:
    url = API_URL_FORMAT.format(
        year, datasetType.value, surveyType.value) + route
    return requests.get(url).json()

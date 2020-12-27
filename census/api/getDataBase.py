from api.constants import API_URL_FORMAT
from models import SurveyType
import requests
from typing import Any


def getDataBase(year: int, route: str = '', surveyType='') -> Any:
    url = API_URL_FORMAT.format(year, surveyType.value)
    return requests.get(url + route).json()

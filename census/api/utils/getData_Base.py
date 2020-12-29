from typing import Any

import requests

from api import ApiConfig
from api.constants import API_URL_FORMAT


def getData_Base(apiConfig: ApiConfig,
                 route: str = '') -> Any:
    url = API_URL_FORMAT.format(
        apiConfig.year, apiConfig.datasetType.value, apiConfig.surveyType.value) + route
    return requests.get(url).json()  # type: ignore

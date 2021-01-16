from dataclasses import dataclass
from functools import cache
from typing import Any, Dict, List, cast

import pandas
import pandas as pd
import requests
from tqdm.notebook import tqdm

URL = "https://api.census.gov/data.json"

# documentation: https://www2.census.gov/programs-surveys/acs/tech_docs/subject_definitions/


@dataclass(frozen=True)
class _DatasetsRes:
    year: int
    dataset: List[str]
    isAggregate: bool
    title: str
    description: str

    @classmethod
    def fromJson(cls, jsonRes: Dict[str, Any]):
        return cls(
            cast(int, jsonRes.get("c_vintage")),
            cast(List[str], jsonRes.get("c_dataset")),
            cast(bool, jsonRes.get("c_isAggregate")),
            cast(str, jsonRes.get("title")),
            cast(str, jsonRes.get("description")),
        )


def listAvailableDataSets() -> pd.DataFrame:
    return __listAvailableDataSets()


@cache
def __listAvailableDataSets() -> pd.DataFrame:
    res: Dict[str, Any] = requests.get(URL).json()  # type: ignore
    datasetDicts: List[Dict[str, str]] = []

    availableDatasets: List[_DatasetsRes] = [
        _DatasetsRes.fromJson(datasetJson) for datasetJson in res["dataset"]
    ]

    for dataset in cast(List[_DatasetsRes], tqdm(availableDatasets)):
        # these won't play nice with the tool
        if not dataset.isAggregate:
            continue

        datasetType = ""
        surveyType = ""
        if len(dataset.dataset) > 0:
            datasetType = dataset.dataset[0]
            if len(dataset.dataset) > 1:
                surveyType = "/".join(dataset.dataset[1:])

        datasetDicts.append(
            cast(
                Dict[str, str],
                dict(
                    year=dataset.year,
                    name=dataset.title,
                    description=dataset.description,
                    datasetType=datasetType,
                    surveyType=surveyType,
                ),
            )
        )

    pandas.set_option("display.max_colwidth", None)  # type: ignore

    return (
        pd.DataFrame(datasetDicts)
        .sort_values(by=["year", "name"], ascending=[False, True])
        .reset_index(drop=True)
    )

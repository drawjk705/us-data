from functools import cache
from typing import Any, Dict, List, cast
import requests
import pandas as pd
from dataclasses import dataclass

URL = "https://api.census.gov/data.json"


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


@cache
def listAvailableDataSets():
    res: Dict[str, Any] = requests.get(URL).json()  # type: ignore
    datasetDicts: List[Dict[str, str]] = []

    availableDatasets: List[_DatasetsRes] = [
        _DatasetsRes.fromJson(datasetJson) for datasetJson in res["dataset"]
    ]

    for dataset in availableDatasets:
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

    return (
        pd.DataFrame(datasetDicts)
        .sort_values(by=["year", "name"], ascending=[False, True])
        .reset_index(drop=True)
    )

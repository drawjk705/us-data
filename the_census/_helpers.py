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
    is_aggregate: bool
    title: str
    description: str

    @classmethod
    def from_json(cls, jsonRes: Dict[str, Any]):
        return cls(
            cast(int, jsonRes.get("c_vintage")),
            cast(List[str], jsonRes.get("c_dataset")),
            cast(bool, jsonRes.get("c_isAggregate")),
            cast(str, jsonRes.get("title")),
            cast(str, jsonRes.get("description")),
        )


def list_available_datasets() -> pd.DataFrame:
    return __list_available_datasets()


@cache
def __list_available_datasets() -> pd.DataFrame:
    res: Dict[str, Any] = requests.get(URL).json()  # type: ignore
    dataset_dicts: List[Dict[str, str]] = []

    available_datasets: List[_DatasetsRes] = [
        _DatasetsRes.from_json(datasetJson) for datasetJson in res["dataset"]
    ]

    for dataset in cast(List[_DatasetsRes], tqdm(available_datasets)):
        # these won't play nice with the tool
        if not dataset.is_aggregate:
            continue

        dataset_type = ""
        survey_type = ""
        if len(dataset.dataset) > 0:
            dataset_type = dataset.dataset[0]
            if len(dataset.dataset) > 1:
                survey_type = "/".join(dataset.dataset[1:])

        dataset_dicts.append(
            cast(
                Dict[str, str],
                dict(
                    year=dataset.year,
                    name=dataset.title,
                    description=dataset.description,
                    dataset=dataset_type,
                    survey=survey_type,
                ),
            )
        )

    pandas.set_option("display.max_colwidth", None)  # type: ignore

    return (
        pd.DataFrame(dataset_dicts)
        .sort_values(by=["year", "name"], ascending=[False, True])
        .reset_index(drop=True)
    )

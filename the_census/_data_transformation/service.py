from collections import OrderedDict
from typing import Any, Dict, List, Tuple, Union, cast

import pandas as pd

from the_census._api.models import GeographyItem
from the_census._config import Config
from the_census._data_transformation.interface import ICensusDataTransformer
from the_census._geographies.models import GeoDomain
from the_census._utils.timer import timer
from the_census._variables.models import Group, GroupVariable, VariableCode


class CensusDataTransformer(ICensusDataTransformer[pd.DataFrame]):

    _config: Config

    def __init__(self, config: Config) -> None:

        self._config = config

    @timer
    def supported_geographies(
        self, supported_geos: OrderedDict[str, GeographyItem]
    ) -> pd.DataFrame:
        values_flattened: List[Dict[str, str]] = []
        for geo_item in supported_geos.values():
            for clause in geo_item.clauses:
                values_flattened.append(
                    {
                        "name": geo_item.name,
                        "hierarchy": geo_item.hierarchy,
                        "for": clause.for_clause,
                        "in": ",".join(clause.in_clauses),
                    }
                )

        return pd.DataFrame(values_flattened)

    @timer
    def geography_codes(self, geo_codes: List[List[str]]) -> pd.DataFrame:
        return (
            pd.DataFrame(geo_codes[1:], columns=geo_codes[0])
            .sort_values(by=geo_codes[0][1:])
            .reset_index(drop=True)
        )

    @timer
    def groups(self, groups: Dict[str, Group]) -> pd.DataFrame:
        group_list = []
        for code, groupObj in groups.items():
            group_dict = {
                "code": code,
                "description": groupObj.description,
                "cleaned_name": groupObj.cleaned_name,
            }
            group_list.append(group_dict)

        return pd.DataFrame(group_list).sort_values(by="code")

    @timer
    def variables(self, variables: List[GroupVariable]) -> pd.DataFrame:
        variable_dict_list: List[Dict[str, Union[str, int, bool]]] = []

        for variable in variables:
            variable_dict_list.append(
                {
                    "code": variable.code,
                    "group_code": variable.group_code,
                    "group_concept": variable.group_concept,
                    "name": variable.name,
                    "predicate_type": variable.predicate_type,
                    "predicate_only": variable.predicate_only,
                    "limit": variable.limit,
                    "cleaned_name": variable.cleaned_name,
                }
            )

        return (
            pd.DataFrame(variable_dict_list)
            .sort_values(by=["code"])
            .reset_index(drop=True)
        )

    @timer
    def stats(
        self,
        results: List[List[List[str]]],
        type_conversions: Dict[str, Any],
        geo_domains_queried: List[GeoDomain],
        column_headers: Dict[VariableCode, str],
        supported_geos: pd.DataFrame,
    ) -> pd.DataFrame:
        main_df = pd.DataFrame()

        mergeKeys = [domain.name for domain in geo_domains_queried]

        for result in results:
            df = pd.DataFrame(result[1:], columns=result[0])

            if main_df.empty:
                main_df = df
            else:
                df = df.drop(columns=["NAME"])  # type: ignore
                main_df = cast(pd.DataFrame, pd.merge(main_df, df, on=mergeKeys, how="inner"))  # type: ignore

        all_cols = main_df.columns.tolist()

        name_col, sorted_geo_cols, variable_cols = self._partition_stat_columns(
            column_headers,
            all_cols,
            supported_geos,
        )

        reorderedColumns = name_col + sorted_geo_cols + variable_cols

        return (
            main_df[reorderedColumns]  # type: ignore
            .astype(type_conversions)
            .rename(
                columns=column_headers if self._config.replace_column_headers else {}
            )
            .sort_values(by=sorted_geo_cols)
            .reset_index(drop=True)
        )

    def _partition_stat_columns(
        self,
        renamed_column_headers: Dict[VariableCode, str],
        df_columns: List[str],
        supported_geos: pd.DataFrame,
    ) -> Tuple[List[str], List[str], List[str]]:
        originalVariableHeaders = [str(col) for col in renamed_column_headers.keys()]
        nameHeader = ["NAME"]

        geo_cols = [
            col for col in df_columns if col not in nameHeader + originalVariableHeaders
        ]
        sorted_geo_cols = [
            domain.name
            for domain in self._sort_geo_domains(
                [GeoDomain(col) for col in geo_cols], supported_geos
            )
        ]

        variable_cols = [
            col for col in df_columns if col != "NAME" and col not in geo_cols
        ]

        return nameHeader, sorted_geo_cols, variable_cols

    def _sort_geo_domains(
        self,
        geo_domains: List[GeoDomain],
        supported_geos: pd.DataFrame,
    ) -> List[GeoDomain]:
        geoHierarchyMapping: List[Dict[str, str]] = (
            supported_geos[["name", "hierarchy"]].drop_duplicates().to_dict("records")
        )
        geoNameToHierarchy = {
            mapping["name"]: mapping["hierarchy"] for mapping in geoHierarchyMapping
        }

        return sorted(
            geo_domains, key=lambda geoDomain: geoNameToHierarchy[geoDomain.name]
        )

from collections import OrderedDict
from typing import Any, Dict
from unittest.mock import MagicMock, Mock

import numpy as np
import pandas as pd
import pytest
from pytest_mock import MockFixture

from tests.service_test_fixtures import ServiceTestFixture
from the_census._api.models import GeographyClauseSet, GeographyItem
from the_census._data_transformation.service import CensusDataTransformer
from the_census._geographies.models import GeoDomain
from the_census._variables.models import Group, GroupCode, GroupVariable, VariableCode


@pytest.fixture
def pandas_mock(mocker: MockFixture) -> Mock:
    return mocker.patch("pandas.DataFrame")


class TestCensusDataTransformer(ServiceTestFixture[CensusDataTransformer]):
    def test_supported_geographies(self, pandas_mock: MagicMock):
        supported_geos = OrderedDict(
            {
                "abc": GeographyItem.makeItem(
                    name="abc",
                    hierarchy="123",
                    clauses=[
                        GeographyClauseSet.makeSet(
                            for_clause="banana", in_clauses=["apple"]
                        )
                    ],
                ),
                "def": GeographyItem.makeItem(
                    name="def",
                    hierarchy="567",
                    clauses=[
                        GeographyClauseSet.makeSet(
                            for_clause="chair", in_clauses=["stool", "table"]
                        ),
                        GeographyClauseSet.makeSet(
                            for_clause="elf", in_clauses=["santa", "workshop"]
                        ),
                    ],
                ),
            }
        )
        expectedCallValues = [
            {"name": "abc", "hierarchy": "123", "for": "banana", "in": "apple"},
            {"name": "def", "hierarchy": "567", "for": "chair", "in": "stool,table"},
            {"name": "def", "hierarchy": "567", "for": "elf", "in": "santa,workshop"},
        ]

        self._service.supported_geographies(supported_geos)

        pandas_mock.assert_called_once_with(expectedCallValues)

    def test_geography_codes(self, pandas_mock: Mock):
        headers = ["header 1", "header 2"]
        rows = [["1", "2"], ["3", "4"], ["5", "6"]]
        geo_codes = [headers] + rows

        self._service.geography_codes(geo_codes)

        pandas_mock.assert_called_once_with(rows, columns=headers)

    def test_group_data(self, pandas_mock: Mock):
        group_data = {
            "1": Group.from_json(dict(name="1", description="desc1")),
            "2": Group.from_json(dict(name="1", description="desc2")),
        }
        expectedCalledWith = [
            {"code": "1", "description": "desc1", "cleaned_name": "Desc1"},
            {"code": "2", "description": "desc2", "cleaned_name": "Desc2"},
        ]

        self._service.groups(group_data)

        pandas_mock.assert_called_once_with(expectedCalledWith)

    def test_variables(self, pandas_mock: Mock):
        variables = [
            GroupVariable(
                code=VariableCode("123"),
                group_code=GroupCode("g123"),
                group_concept="gCon1",
                name="name1",
                limit=1,
                predicate_only=True,
                predicate_type="string",
            ),
            GroupVariable(
                code=VariableCode("456"),
                group_code=GroupCode("g456"),
                group_concept="gCon2",
                name="name2",
                limit=2,
                predicate_only=False,
                predicate_type="int",
            ),
        ]
        expectedCall = [
            {
                "cleaned_name": "",
                "code": "123",
                "group_code": "g123",
                "group_concept": "gCon1",
                "limit": 1,
                "name": "name1",
                "predicate_only": True,
                "predicate_type": "string",
            },
            {
                "cleaned_name": "",
                "code": "456",
                "group_code": "g456",
                "group_concept": "gCon2",
                "limit": 2,
                "name": "name2",
                "predicate_only": False,
                "predicate_type": "int",
            },
        ]

        self._service.variables(variables)

        pandas_mock.assert_called_once_with(expectedCall)

    def test_partition_stats_columns(self):
        allsupported_geos = pd.DataFrame(
            [
                dict(name="one place", hierarchy=1),
                dict(name="two place", hierarchy=2),
                dict(name="three place", hierarchy=3),
                dict(name="four place", hierarchy=4),
                dict(name="five place", hierarchy=5),
            ]
        )
        renamedColHeaders = {VariableCode("abc"): "Abc", VariableCode("def"): "Def"}
        dfColumns = [
            "NAME",
            "five place",
            "abc",
            "def",
            "one place",
            "three place",
            "two place",
            "four place",
        ]
        expectedsorted_geo_cols = [
            "one place",
            "two place",
            "three place",
            "four place",
            "five place",
        ]

        self.mocker.patch.object(
            self._service,
            "_sort_geo_domains",
            return_value=[GeoDomain(col) for col in expectedsorted_geo_cols],
        )

        res = self._service._partition_stat_columns(
            renamedColHeaders, dfColumns, allsupported_geos
        )

        assert res == (["NAME"], expectedsorted_geo_cols, ["abc", "def"])

    def test_sort_geo_domains(self):
        allsupported_geos = pd.DataFrame(
            [
                dict(name="one place", hierarchy=1),
                dict(name="two place", hierarchy=2),
                dict(name="three place", hierarchy=3),
            ]
        )
        geo_domains = [
            GeoDomain(place) for place in ["two place", "one place", "three place"]
        ]

        res = self._service._sort_geo_domains(geo_domains, allsupported_geos)

        assert res == [
            GeoDomain(place) for place in ["one place", "two place", "three place"]
        ]

    @pytest.mark.parametrize("should_replace_column_headers", [True, False])
    def test_stats(self, should_replace_column_headers: bool):
        supported_geos = pd.DataFrame(
            [dict(name="geoCol1", hierarchy=1), dict(name="geoCol2", hierarchy=2)]
        )
        results = [
            [
                ["NAME", "var1", "var2", "geoCol1", "geoCol2"],
                ["1", "5", "1.2", "4", "5"],
                ["6", "6", "4.2", "9", "10"],
            ],
            [
                ["NAME", "var3", "var4", "geoCol1", "geoCol2"],
                ["1", "stringy", "tassel", "4", "5"],
                ["6", "yarn", "ropy", "9", "10"],
            ],
        ]

        type_conversions: Dict[str, Any] = dict(var1=int, var2=float)
        column_headers: Dict[VariableCode, str] = dict(
            var1="banana", var2="apple", var3="pear", var4="peach"
        )
        geo_domains = [GeoDomain("geoCol1"), GeoDomain("geoCol2")]

        self.mocker.patch.object(
            self._service,
            "_partition_stat_columns",
            return_value=(
                ["NAME"],
                ["geoCol1", "geoCol2"],
                ["var1", "var2", "var3", "var4"],
            ),
        )
        self.mocker.patch.object(
            self._service._config,
            "replace_column_headers",
            should_replace_column_headers,
        )

        res = self._service.stats(
            results, type_conversions, geo_domains, column_headers, supported_geos
        )

        if should_replace_column_headers:
            assert res.dtypes.to_dict() == {  # type: ignore
                "NAME": np.dtype("O"),
                "apple": np.dtype("float64"),
                "banana": np.dtype("int64"),
                "geoCol1": np.dtype("O"),
                "geoCol2": np.dtype("O"),
                "peach": np.dtype("O"),
                "pear": np.dtype("O"),
            }
            assert res.columns.tolist() == [
                "NAME",
                "geoCol1",
                "geoCol2",
                "banana",
                "apple",
                "pear",
                "peach",
            ]
        else:
            assert res.dtypes.to_dict() == {  # type: ignore
                "NAME": np.dtype("O"),
                "var2": np.dtype("float64"),
                "var1": np.dtype("int64"),
                "geoCol1": np.dtype("O"),
                "geoCol2": np.dtype("O"),
                "var4": np.dtype("O"),
                "var3": np.dtype("O"),
            }
            assert res.columns.tolist() == [
                "NAME",
                "geoCol1",
                "geoCol2",
                "var1",
                "var2",
                "var3",
                "var4",
            ]

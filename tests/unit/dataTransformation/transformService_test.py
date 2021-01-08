# pyright: reportMissingTypeStubs=false

from tests.utils import shuffledCases
from census.geographies.models import GeoDomain
from typing import Any, Dict, Optional
import numpy as np
from census.variables.models import Group, GroupVariable, GroupCode, VariableCode
from census.dataTransformation.service import DataFrameTransformer
from tests.serviceTestFixtures import ServiceTestFixture
from census.api.models import GeographyClauseSet, GeographyItem
from collections import OrderedDict
from unittest.mock import MagicMock, Mock

import pytest
from pytest_mock import MockFixture


@pytest.fixture
def pandasMock(mocker: MockFixture) -> Mock:
    return mocker.patch("pandas.DataFrame")


class TestDataFrameTransformer(ServiceTestFixture[DataFrameTransformer]):

    serviceType = DataFrameTransformer

    def test_supportedGeographies(self, pandasMock: MagicMock):
        supportedGeos = OrderedDict(
            {
                "abc": GeographyItem.makeItem(
                    name="abc",
                    hierarchy="123",
                    clauses=[
                        GeographyClauseSet.makeSet(
                            forClause="banana", inClauses=["apple"]
                        )
                    ],
                ),
                "def": GeographyItem.makeItem(
                    name="def",
                    hierarchy="567",
                    clauses=[
                        GeographyClauseSet.makeSet(
                            forClause="chair", inClauses=["stool", "table"]
                        ),
                        GeographyClauseSet.makeSet(
                            forClause="elf", inClauses=["santa", "workshop"]
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

        self._service.supportedGeographies(supportedGeos)

        pandasMock.assert_called_once_with(expectedCallValues)

    def test_geographyCodes(self, pandasMock: Mock):
        headers = ["header 1", "header 2"]
        rows = [["1", "2"], ["3", "4"], ["5", "6"]]
        geoCodes = [headers] + rows

        self._service.geographyCodes(geoCodes)

        pandasMock.assert_called_once_with(rows, columns=headers)

    def test_groupData(self, pandasMock: Mock):
        groupData = {
            "1": Group(code=GroupCode("1"), description="desc1"),
            "2": Group(code=GroupCode("2"), description="desc2"),
        }
        expectedCalledWith = [
            {"code": "1", "description": "desc1"},
            {"code": "2", "description": "desc2"},
        ]

        self._service.groups(groupData)

        pandasMock.assert_called_once_with(expectedCalledWith)

    def test_variables(self, pandasMock: Mock):
        variables = [
            GroupVariable(
                code=VariableCode("123"),
                groupCode=GroupCode("g123"),
                groupConcept="gCon1",
                name="name1",
                limit=1,
                predicateOnly=True,
                predicateType="string",
            ),
            GroupVariable(
                code=VariableCode("456"),
                groupCode=GroupCode("g456"),
                groupConcept="gCon2",
                name="name2",
                limit=2,
                predicateOnly=False,
                predicateType="int",
            ),
        ]
        expectedCall = [
            {
                "code": "123",
                "groupCode": "g123",
                "groupConcept": "gCon1",
                "name": "name1",
                "limit": 1,
                "predicateOnly": True,
                "predicateType": "string",
            },
            {
                "code": "456",
                "groupCode": "g456",
                "groupConcept": "gCon2",
                "name": "name2",
                "limit": 2,
                "predicateOnly": False,
                "predicateType": "int",
            },
        ]

        self._service.variables(variables)

        pandasMock.assert_called_once_with(expectedCall)

    @pytest.mark.parametrize(*shuffledCases(shouldUseColumnHeaders=[True, False]))
    def test_stats(self, shouldUseColumnHeaders: bool):
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

        typeConversions: Dict[str, Any] = dict(var1=int, var2=float)
        columnHeaders: Optional[Dict[VariableCode, str]] = (
            dict(var1="banana", var2="apple", var3="pear", var4="peach")
            if shouldUseColumnHeaders
            else None
        )
        geoDomains = [GeoDomain("geoCol1"), GeoDomain("geoCol2")]

        res = self._service.stats(results, typeConversions, geoDomains, columnHeaders)

        if shouldUseColumnHeaders:
            assert res.dtypes.to_dict() == {
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
            assert res.dtypes.to_dict() == {
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

from census.dataTransformation.toDataFrame import DataFrameTransformer
from tests.base import FixtureNames, ServiceTestFixture
from census.api.models import GeographyClauseSet, GeographyItem, Group, GroupVariable
from collections import OrderedDict
from unittest.mock import MagicMock, Mock

import pytest
from pytest_mock import MockFixture


@pytest.fixture
def pandasMock(mocker: MockFixture) -> Mock:
    return mocker.patch("pandas.DataFrame")


@pytest.mark.usefixtures(FixtureNames.serviceFixture)
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
            "1": Group(name="1", description="desc1"),
            "2": Group(name="2", description="desc2"),
        }
        expectedCalledWith = [
            {"code": "1", "description": "desc1"},
            {"code": "2", "description": "desc2"},
        ]

        self._service.groupData(groupData)

        pandasMock.assert_called_once_with(expectedCalledWith)

    def test_variables(self, pandasMock: Mock):
        variables = [
            GroupVariable(
                code="123",
                groupCode="g123",
                groupConcept="gCon1",
                name="name1",
                limit=1,
                predicateOnly=True,
                predicateType="string",
            ),
            GroupVariable(
                code="456",
                groupCode="g456",
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
                "concept": "gCon1",
                "name": "name1",
                "limit": 1,
                "predicateOnly": True,
                "predicateType": "pt1",
            },
            {
                "code": "456",
                "groupCode": "g456",
                "concept": "gCon2",
                "name": "name2",
                "limit": 2,
                "predicateOnly": False,
                "predicateType": "pt2",
            },
        ]

        self._service.variables(variables)

        pandasMock.assert_called_once_with(expectedCall)

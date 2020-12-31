from census.dataTransformation.dataFrame import DataFrameTransformer
from census.api.models import GeographyClauseSet, GeographyItem, Group, GroupVariable
from collections import OrderedDict
from unittest.mock import Mock

import pytest
from pytest_mock import MockFixture


@pytest.fixture
def pandasMock(mocker: MockFixture) -> Mock:
    return mocker.patch("pandas.DataFrame")


@pytest.fixture
def service() -> DataFrameTransformer:
    return DataFrameTransformer()


def test_supportedGeographies(service: DataFrameTransformer, pandasMock: Mock):
    supportedGeos = OrderedDict(
        {
            "abc": GeographyItem.makeItem(
                name="abc",
                hierarchy="123",
                clauses=[
                    GeographyClauseSet.makeSet(forClause="banana", inClauses=["apple"])
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

    service.supportedGeographies(supportedGeos)

    pandasMock.assert_called_once_with(expectedCallValues)


def test_geographyCodes(service: DataFrameTransformer, pandasMock: Mock):
    headers = ["header 1", "header 2"]
    rows = [["1", "2"], ["3", "4"], ["5", "6"]]
    geoCodes = [headers] + rows

    service.geographyCodes(geoCodes)

    pandasMock.assert_called_once_with(rows, columns=headers)


def test_groupData(service: DataFrameTransformer, pandasMock: Mock):
    groupData = {
        "1": Group(name="1", description="desc1"),
        "2": Group(name="2", description="desc2"),
    }
    expectedCalledWith = [
        {"code": "1", "description": "desc1"},
        {"code": "2", "description": "desc2"},
    ]

    service.groupData(groupData)

    pandasMock.assert_called_once_with(expectedCalledWith)


def test_variables(service: DataFrameTransformer, pandasMock: Mock):
    variables = [
        GroupVariable(
            code="123",
            groupCode="g123",
            groupConcept="gCon1",
            name="name1",
            limit=1,
            predicateOnly=True,
            predicateType="pt1",
        ),
        GroupVariable(
            code="456",
            groupCode="g456",
            groupConcept="gCon2",
            name="name2",
            limit=2,
            predicateOnly=False,
            predicateType="pt2",
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

    service.variables(variables)

    pandasMock.assert_called_once_with(expectedCall)

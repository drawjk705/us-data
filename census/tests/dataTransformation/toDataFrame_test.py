# from census.api.models import GeographyClauseSet, GeographyItem
# from collections import OrderedDict
# from unittest.mock import Mock

# import pandas
# import census.dataTransformation.toDataFrame as toDf
# import pytest
# from pytest_mock import MockFixture


# @pytest.fixture
# def pandasMock(mocker: MockFixture) -> Mock:
#     mocker.patch("pandas.DataFrame")

#     return pandas.DataFrame  # type: ignore


# def test_supportedGeographies(pandasMock: Mock):
#     supportedGeos = OrderedDict(
#         {
#             "abc": GeographyItem.makeItem(
#                 name="abc",
#                 hierarchy="123",
#                 clauses=[
#                     GeographyClauseSet.makeSet(forClause="banana", inClauses=["apple"])
#                 ],
#             ),
#             "def": GeographyItem.makeItem(
#                 name="def",
#                 hierarchy="567",
#                 clauses=[
#                     GeographyClauseSet.makeSet(
#                         forClause="chair", inClauses=["table", "stool"]
#                     ),
#                     GeographyClauseSet.makeSet(
#                         forClause="elf", inClauses=["santa", "workshop"]
#                     ),
#                 ],
#             ),
#         }
#     )
#     expectedCallValues = [
#         {"name": "abc", "hierarchy": "123", "for": "banana", "in": "apple"},
#         {"name": "def", "hierarchy": "567", "for": "chair", "in": "stool,table"},
#         {"name": "def", "hierarchy": "567", "for": "elf", "in": "santa,workshop"},
#     ]

#     toDf.supportedGeographies(supportedGeos)

#     pandasMock.assert_called_once_with(expectedCallValues)
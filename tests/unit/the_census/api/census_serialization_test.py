from typing import Any, Dict, OrderedDict, Union

import hypothesis.strategies as st
import pytest
from hypothesis import assume
from hypothesis.core import given

from the_census._api.models import GeographyClauseSet, GeographyItem
from the_census._api.serialization import ApiSerializationService
from the_census._variables.models import Group, GroupCode, GroupVariable


@pytest.fixture
def service() -> ApiSerializationService:
    return ApiSerializationService()


@given(
    varCode1=st.text(),
    varCode2=st.text(),
    var1=st.fixed_dictionaries(
        {
            "label": st.text(),
            "concept": st.text(),
            "predicateType": st.text(),
            "group": st.text(),
            "limit": st.integers(),
            "predicateOnly": st.booleans(),
        }
    ),
    var2=st.fixed_dictionaries(
        {
            "label": st.text(),
            "concept": st.text(),
            "predicateType": st.text(),
            "group": st.text(),
            "limit": st.integers(),
            "predicateOnly": st.booleans(),
        }
    ),
)
def test_parseVariableData(
    varCode1: str,
    varCode2: str,
    var1: Dict[str, Union[str, int, bool]],
    var2: Dict[str, Union[str, int, bool]],
):
    assume(varCode1 != varCode2)

    service = ApiSerializationService()
    variables = {"variables": {varCode1: var1, varCode2: var2}}
    expectedVar1 = GroupVariable.fromJson(varCode1, var1)
    expectedVar2 = GroupVariable.fromJson(varCode2, var2)
    expected = [expectedVar1, expectedVar2]

    actual = service.parseGroupVariables(variables)

    assert actual == expected


__supportedGeosTestCases = [
    (
        {
            "fips": [
                {
                    "name": "principal city (or part)",
                    "geoLevelDisplay": "312",
                    "referenceDate": "2019-01-01",
                    "requires": [
                        "metropolitan statistical area/micropolitan statistical area",
                        "state (or part)",
                    ],
                }
            ]
        },
        OrderedDict(
            {
                "principal city (or part)": GeographyItem.makeItem(
                    name="principal city (or part)",
                    hierarchy="312",
                    clauses=[
                        GeographyClauseSet.makeSet(
                            forClause="principal city (or part):CODE",
                            inClauses=[
                                "metropolitan statistical area/micropolitan statistical area:CODE",
                                "state (or part):CODE",
                            ],
                        ),
                        GeographyClauseSet.makeSet(
                            forClause="principal city (or part):*",
                            inClauses=[
                                "metropolitan statistical area/micropolitan statistical area:CODE",
                                "state (or part):CODE",
                            ],
                        ),
                    ],
                )
            }
        ),
    ),
    (
        {
            "fips": [
                {
                    "name": "congressional district",
                    "geoLevelDisplay": "500",
                    "referenceDate": "2019-01-01",
                    "requires": ["state"],
                    "wildcard": ["state"],
                    "optionalWithWCFor": "state",
                }
            ]
        },
        OrderedDict(
            {
                "congressional district": GeographyItem.makeItem(
                    name="congressional district",
                    hierarchy="500",
                    clauses=[
                        GeographyClauseSet.makeSet(
                            forClause="congressional district:CODE",
                            inClauses=["state:CODE"],
                        ),
                        GeographyClauseSet.makeSet(
                            forClause="congressional district:*", inClauses=[]
                        ),
                        GeographyClauseSet.makeSet(
                            forClause="congressional district:*",
                            inClauses=["state:*"],
                        ),
                    ],
                ),
            }
        ),
    ),
    ([], OrderedDict({})),
]


@pytest.mark.parametrize(["apiResponse", "expected"], __supportedGeosTestCases)
def test_parseSupportedGeographies(
    service: ApiSerializationService,
    apiResponse: Dict[Any, Any],
    expected: GeographyItem,
):
    actual = service.parseSupportedGeographies(apiResponse)

    assert actual == expected


@pytest.mark.parametrize(
    ["groupResponse", "expected"],
    [
        (
            {
                "groups": [
                    {
                        "name": "B17015",
                        "description": "POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                        "variables": "https://api.census.gov/data/2019/acs/acs1/groups/B17015.json",
                    },
                    {
                        "name": "B18104",
                        "description": "SEX BY AGE BY COGNITIVE DIFFICULTY",
                        "variables": "https://api.census.gov/data/2019/acs/acs1/groups/B18104.json",
                    },
                ]
            },
            {
                "B17015": Group(
                    code=GroupCode("B17015"),
                    description="POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                    variables="https://api.census.gov/data/2019/acs/acs1/groups/B17015.json",
                    cleanedName="PovertyStatusInThePast12MonthsOfFamiliesByFamilyTypeBySocialSecurityIncomeBySupplementalSecurityIncomeSsiAndCashPublicAssistanceIncome",
                ),
                "B18104": Group(
                    code=GroupCode("B18104"),
                    description="SEX BY AGE BY COGNITIVE DIFFICULTY",
                    variables="https://api.census.gov/data/2019/acs/acs1/groups/B18104.json",
                    cleanedName="SexByAgeByCognitiveDifficulty",
                ),
            },
        ),
        ([], {}),
    ],
)
def test_parseGroups(
    service: ApiSerializationService,
    groupResponse: Dict[Any, Any],
    expected: Dict[str, Group],
):
    actual = service.parseGroups(groupResponse)

    assert actual == expected

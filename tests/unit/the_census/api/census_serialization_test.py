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
            "predicate_type": st.text(),
            "group": st.text(),
            "limit": st.integers(),
            "predicate_only": st.booleans(),
        }
    ),
    var2=st.fixed_dictionaries(
        {
            "label": st.text(),
            "concept": st.text(),
            "predicate_type": st.text(),
            "group": st.text(),
            "limit": st.integers(),
            "predicate_only": st.booleans(),
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
    expectedVar1 = GroupVariable.from_json(varCode1, var1)
    expectedVar2 = GroupVariable.from_json(varCode2, var2)
    expected = [expectedVar1, expectedVar2]

    actual = service.parse_group_variables(variables)

    assert actual == expected


__supported_geosTestCases = [
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
                            for_clause="principal city (or part):CODE",
                            in_clauses=[
                                "metropolitan statistical area/micropolitan statistical area:CODE",
                                "state (or part):CODE",
                            ],
                        ),
                        GeographyClauseSet.makeSet(
                            for_clause="principal city (or part):*",
                            in_clauses=[
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
                            for_clause="congressional district:CODE",
                            in_clauses=["state:CODE"],
                        ),
                        GeographyClauseSet.makeSet(
                            for_clause="congressional district:*", in_clauses=[]
                        ),
                        GeographyClauseSet.makeSet(
                            for_clause="congressional district:*",
                            in_clauses=["state:*"],
                        ),
                    ],
                ),
            }
        ),
    ),
    ([], OrderedDict({})),
]


@pytest.mark.parametrize(["apiResponse", "expected"], __supported_geosTestCases)
def test_parse_supported_geographies(
    service: ApiSerializationService,
    apiResponse: Dict[Any, Any],
    expected: GeographyItem,
):
    actual = service.parse_supported_geographies(apiResponse)

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
                    cleaned_name="PovertyStatusInThePast12MonthsOfFamiliesByFamilyTypeBySocialSecurityIncomeBySupplementalSecurityIncomeSsiAndCashPublicAssistanceIncome",
                ),
                "B18104": Group(
                    code=GroupCode("B18104"),
                    description="SEX BY AGE BY COGNITIVE DIFFICULTY",
                    variables="https://api.census.gov/data/2019/acs/acs1/groups/B18104.json",
                    cleaned_name="SexByAgeByCognitiveDifficulty",
                ),
            },
        ),
        ([], {}),
    ],
)
def test_parse_groups(
    service: ApiSerializationService,
    groupResponse: Dict[Any, Any],
    expected: Dict[str, Group],
):
    actual = service.parse_groups(groupResponse)

    assert actual == expected

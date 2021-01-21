import os
import re
import shutil
from pathlib import Path
from typing import Any, Collection, Dict, Generator, List, Optional, Set, cast

import pandas
import pytest
import requests
from pytest import MonkeyPatch
from pytest_mock import MockerFixture

from tests.integration.census.mockApiResponses import MOCK_API
from tests.utils import MockRes
from the_census import Census, GeoDomain
from the_census._exceptions import CensusDoesNotExistException, NoCensusApiKeyException
from the_census._utils.cleanVariableName import cleanVariableName
from the_census._variables.models import Group, GroupCode, GroupVariable, VariableCode
from the_census._variables.repository.models import GroupSet, VariableSet

# pyright: reportUnknownMemberType=false


expectedStatsResWithoutNames = [
    {
        "B17015_001E": 172441.0,
        "B18104_001E": 664816.0,
        "B18105_001E": 664816.0,
        "NAME": "Congressional District 1 (116th Congress), Alabama",
        "congressional district": "01",
        "state": "01",
    },
    {
        "B17015_001E": 168129.0,
        "B18104_001E": 610312.0,
        "B18105_001E": 610312.0,
        "NAME": "Congressional District 2 (116th Congress), Alabama",
        "congressional district": "02",
        "state": "01",
    },
    {
        "B17015_001E": 184320.0,
        "B18104_001E": 664930.0,
        "B18105_001E": 664930.0,
        "NAME": "Congressional District 3 (116th Congress), Alabama",
        "congressional district": "03",
        "state": "01",
    },
    {
        "B17015_001E": 179508.0,
        "B18104_001E": 640347.0,
        "B18105_001E": 640347.0,
        "NAME": "Congressional District 4 (116th Congress), Alabama",
        "congressional district": "04",
        "state": "01",
    },
    {
        "B17015_001E": 195668.0,
        "B18104_001E": 681411.0,
        "B18105_001E": 681411.0,
        "NAME": "Congressional District 5 (116th Congress), Alabama",
        "congressional district": "05",
        "state": "01",
    },
    {
        "B17015_001E": 186592.0,
        "B18104_001E": 653559.0,
        "B18105_001E": 653559.0,
        "NAME": "Congressional District 6 (116th Congress), Alabama",
        "congressional district": "06",
        "state": "01",
    },
    {
        "B17015_001E": 151225.0,
        "B18104_001E": 620542.0,
        "B18105_001E": 620542.0,
        "NAME": "Congressional District 7 (116th Congress), Alabama",
        "congressional district": "07",
        "state": "01",
    },
]

expectedStatsResWithNames = [
    {
        "Estimate_Total_B17015": 172441.0,
        "Estimate_Total_B18104": 664816.0,
        "Estimate_Total_B18105": 664816.0,
        "NAME": "Congressional District 1 (116th Congress), Alabama",
        "congressional district": "01",
        "state": "01",
    },
    {
        "Estimate_Total_B17015": 168129.0,
        "Estimate_Total_B18104": 610312.0,
        "Estimate_Total_B18105": 610312.0,
        "NAME": "Congressional District 2 (116th Congress), Alabama",
        "congressional district": "02",
        "state": "01",
    },
    {
        "Estimate_Total_B17015": 184320.0,
        "Estimate_Total_B18104": 664930.0,
        "Estimate_Total_B18105": 664930.0,
        "NAME": "Congressional District 3 (116th Congress), Alabama",
        "congressional district": "03",
        "state": "01",
    },
    {
        "Estimate_Total_B17015": 179508.0,
        "Estimate_Total_B18104": 640347.0,
        "Estimate_Total_B18105": 640347.0,
        "NAME": "Congressional District 4 (116th Congress), Alabama",
        "congressional district": "04",
        "state": "01",
    },
    {
        "Estimate_Total_B17015": 195668.0,
        "Estimate_Total_B18104": 681411.0,
        "Estimate_Total_B18105": 681411.0,
        "NAME": "Congressional District 5 (116th Congress), Alabama",
        "congressional district": "05",
        "state": "01",
    },
    {
        "Estimate_Total_B17015": 186592.0,
        "Estimate_Total_B18104": 653559.0,
        "Estimate_Total_B18105": 653559.0,
        "NAME": "Congressional District 6 (116th Congress), Alabama",
        "congressional district": "06",
        "state": "01",
    },
    {
        "Estimate_Total_B17015": 151225.0,
        "Estimate_Total_B18104": 620542.0,
        "Estimate_Total_B18105": 620542.0,
        "NAME": "Congressional District 7 (116th Congress), Alabama",
        "congressional district": "07",
        "state": "01",
    },
]


def verifyResource(
    resource: str,
    exists: bool = True,
    expectedData: Optional[List[Dict[str, Any]]] = None,
):
    path = Path(f"cache/2019/acs/acs1/{resource}")

    if not exists:
        assert not path.exists()
    else:
        assert path.exists()

        if expectedData:
            df = pandas.read_csv(path)  # type: ignore
            assert df.to_dict("records") == expectedData


@pytest.fixture(scope="function", autouse=True)
def apiCalls(monkeypatch: MonkeyPatch) -> Set[str]:
    _apiCalls: Set[str] = set()

    def mockGet(route: str):
        routeWithoutKey = re.sub(r"(\?|&)key=.*", "", route)
        _apiCalls.add(routeWithoutKey)
        res = cast(Collection[Any], MOCK_API.get(routeWithoutKey))
        status_code = 404 if res is None else 200
        return MockRes(status_code, res)

    monkeypatch.setattr(requests, "get", mockGet)

    return _apiCalls


@pytest.fixture(scope="function", autouse=True)
def setPathToTest() -> Generator[None, None, None]:
    parentPath = Path(__file__).parent.absolute()

    os.chdir(parentPath)

    tempDir = Path("temp")
    if tempDir.exists():
        shutil.rmtree(tempDir)

    tempDir.mkdir(parents=True, exist_ok=False)

    os.chdir(tempDir.absolute())

    try:
        yield
    finally:
        os.chdir(parentPath)
        shutil.rmtree(tempDir.absolute())


@pytest.fixture
def givenCacheWithGroup() -> None:
    Path("cache/2019/acs/acs1/").mkdir(parents=True, exist_ok=True)
    pandas.DataFrame(
        [
            dict(code="abc", description="alphabet", cleanedName="Alphabet"),
            dict(code="123", description="numbers", cleanedName="Numbers"),
        ]
    ).to_csv("./cache/2019/acs/acs1/groups.csv")
    verifyResource("groups.csv")


@pytest.fixture
def givenCacheWithVariables() -> None:
    Path("cache/2019/acs/acs1/variables/").mkdir(parents=True, exist_ok=True)
    pandas.DataFrame(
        [
            dict(
                code="v1",
                groupCode="g1",
                groupConcept="group 1",
                name="variable 1",
                predicateType="int",
                predicateOnly=True,
                limit=0,
                cleanedName="Variable 1",
            ),
            dict(
                code="v2",
                groupCode="g1",
                groupConcept="group 1",
                name="variable 2",
                predicateType="int",
                predicateOnly=True,
                limit=0,
                cleanedName="Variable 2",
            ),
        ]
    ).to_csv("./cache/2019/acs/acs1/variables/varsForGroup.csv")
    verifyResource("variables/varsForGroup.csv")


@pytest.fixture(autouse=True)
def givenEnvVar(mocker: MockerFixture):
    mocker.patch.object(os, "getenv", return_value="banana")


@pytest.mark.integration
class TestCensus:
    def test_census_givenInvalidDataRequest(self):
        with pytest.raises(
            CensusDoesNotExistException,
            match="Data does not exist for dataset=acs; survey=acs1; year=2020",
        ):
            _ = Census(2020)

    def test_census_givenNoEnvironmentVariable(self, mocker: MockerFixture):
        mocker.patch.object(os, "getenv", return_value=None)
        with pytest.raises(
            NoCensusApiKeyException, match="Could not find `CENSUS_API_KEY` in .env"
        ):
            _ = Census(2019)

    def test_census_givenNotCachingOnDiskAndNoLoadingFromDisk_doesNotCreateCache(
        self,
    ):
        _ = Census(2019, shouldLoadFromExistingCache=False, shouldCacheOnDisk=False)

        assert not Path("cache").exists()

    def test_census_givenCensusDoesNotLoadFromExistingCache_purgesExistingCache(
        self, givenCacheWithGroup: None
    ):
        _ = Census(2019, shouldLoadFromExistingCache=False, shouldCacheOnDisk=True)

        assert Path("cache").exists()
        assert len(list(Path("cache/2019/acs/acs1").iterdir())) == 0

    def test_census_createsCacheAndLoadsItOnQuery(
        self, apiCalls: Set[str], givenCacheWithGroup: None
    ):
        census = Census(2019, shouldLoadFromExistingCache=True, shouldCacheOnDisk=True)

        census.getGroups()

        assert "https://api.census.gov/data/2019/acs/acs1/groups.json" not in apiCalls
        assert len(apiCalls) == 1

        assert Path("cache").exists()

    def test_census_getGeographyCodes(
        self,
    ):
        census = Census(2019)

        codes = census.getGeographyCodes(
            GeoDomain("congressional district"),
            GeoDomain("state", "01"),
        )

        expected = [
            {
                "NAME": "Congressional District 1 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "01",
            },
            {
                "NAME": "Congressional District 2 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "02",
            },
            {
                "NAME": "Congressional District 3 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "03",
            },
            {
                "NAME": "Congressional District 4 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "04",
            },
            {
                "NAME": "Congressional District 5 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "05",
            },
            {
                "NAME": "Congressional District 6 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "06",
            },
            {
                "NAME": "Congressional District 7 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "07",
            },
        ]

        assert codes.to_dict("records") == expected

    def test_census_groupsAndVariables(self):
        census = Census(2019, shouldCacheOnDisk=True)
        verifyResource("groups.csv", exists=False)

        _ = census.getGroups()

        groupCodes = list(census.groups.values())
        verifyResource("groups.csv")
        assert len(groupCodes) == 3

        for code in groupCodes:
            verifyResource(f"variables/{code}.csv", exists=False)

        variables = census.getVariablesByGroup(*groupCodes)
        variables["cleanedName"] = variables["name"].apply(cleanVariableName)
        for code in groupCodes:
            verifyResource(
                f"variables/{code}.csv",
                exists=True,
                expectedData=[
                    variable
                    for variable in variables.to_dict("records")
                    if variable["groupCode"] == code
                ],
            )

        assert len(census.variables) == 12

    def test_census_getAllVariables(self):
        census = Census(2019, shouldCacheOnDisk=True)
        allVars = census.getAllVariables()

        assert len(allVars.to_dict("records")) == 12
        assert len(census.variables) == 12

        for group, variables in allVars.groupby(["groupCode"]):  # type: ignore
            variables["cleanedName"] = variables["name"].apply(cleanVariableName)
            verifyResource(
                f"variables/{group}.csv",
                exists=True,
                expectedData=variables.to_dict("records"),
            )

    def test_census_groups_populatesGroupNames(self):
        census = Census(2019)

        _ = census.getGroups()

        assert dict(census.groups.items()) == {
            "PovertyStatusInThePast12MonthsOfFamiliesByFamilyTypeBySocialSecurityIncomeBySupplementalSecurityIncomeSsiAndCashPublicAssistanceIncome": "B17015",
            "SexByAgeByAmbulatoryDifficulty": "B18105",
            "SexByAgeByCognitiveDifficulty": "B18104",
        }

    def test_census_variables_populatesVariableNames(self):
        census = Census(2019)

        census.getAllVariables()

        assert dict(census.variables.items()) == {
            "AnnotationOfEstimate_Total_B17015": GroupVariable(
                code=VariableCode("B17015_001EA"),
                groupCode=GroupCode("B17015"),
                groupConcept="POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                name="Annotation of Estimate!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="string",
                cleanedName="AnnotationOfEstimate_Total",
            ),
            "AnnotationOfEstimate_Total_B18104": GroupVariable(
                code=VariableCode("B18104_001EA"),
                groupCode=GroupCode("B18104"),
                groupConcept="SEX BY AGE BY COGNITIVE DIFFICULTY",
                name="Annotation of Estimate!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="string",
                cleanedName="AnnotationOfEstimate_Total",
            ),
            "AnnotationOfEstimate_Total_B18105": GroupVariable(
                code=VariableCode("B18105_001EA"),
                groupCode=GroupCode("B18105"),
                groupConcept="SEX BY AGE BY AMBULATORY DIFFICULTY",
                name="Annotation of Estimate!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="string",
                cleanedName="AnnotationOfEstimate_Total",
            ),
            "AnnotationOfMarginOfError_Total_B17015": GroupVariable(
                code=VariableCode("B17015_001MA"),
                groupCode=GroupCode("B17015"),
                groupConcept="POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                name="Annotation of Margin of Error!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="string",
                cleanedName="AnnotationOfMarginOfError_Total",
            ),
            "AnnotationOfMarginOfError_Total_B18104": GroupVariable(
                code=VariableCode("B18104_001MA"),
                groupCode=GroupCode("B18104"),
                groupConcept="SEX BY AGE BY COGNITIVE DIFFICULTY",
                name="Annotation of Margin of Error!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="string",
                cleanedName="AnnotationOfMarginOfError_Total",
            ),
            "AnnotationOfMarginOfError_Total_B18105": GroupVariable(
                code=VariableCode("B18105_001MA"),
                groupCode=GroupCode("B18105"),
                groupConcept="SEX BY AGE BY AMBULATORY DIFFICULTY",
                name="Annotation of Margin of Error!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="string",
                cleanedName="AnnotationOfMarginOfError_Total",
            ),
            "Estimate_Total_B17015": GroupVariable(
                code=VariableCode("B17015_001E"),
                groupCode=GroupCode("B17015"),
                groupConcept="POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                name="Estimate!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="int",
                cleanedName="Estimate_Total",
            ),
            "Estimate_Total_B18104": GroupVariable(
                code=VariableCode("B18104_001E"),
                groupCode=GroupCode("B18104"),
                groupConcept="SEX BY AGE BY COGNITIVE DIFFICULTY",
                name="Estimate!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="int",
                cleanedName="Estimate_Total",
            ),
            "Estimate_Total_B18105": GroupVariable(
                code=VariableCode("B18105_001E"),
                groupCode=GroupCode("B18105"),
                groupConcept="SEX BY AGE BY AMBULATORY DIFFICULTY",
                name="Estimate!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="int",
                cleanedName="Estimate_Total",
            ),
            "MarginOfError_Total_B17015": GroupVariable(
                code=VariableCode("B17015_001M"),
                groupCode=GroupCode("B17015"),
                groupConcept="POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                name="Margin of Error!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="int",
                cleanedName="MarginOfError_Total",
            ),
            "MarginOfError_Total_B18104": GroupVariable(
                code=VariableCode("B18104_001M"),
                groupCode=GroupCode("B18104"),
                groupConcept="SEX BY AGE BY COGNITIVE DIFFICULTY",
                name="Margin of Error!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="int",
                cleanedName="MarginOfError_Total",
            ),
            "MarginOfError_Total_B18105": GroupVariable(
                code=VariableCode("B18105_001M"),
                groupCode=GroupCode("B18105"),
                groupConcept="SEX BY AGE BY AMBULATORY DIFFICULTY",
                name="Margin of Error!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="int",
                cleanedName="MarginOfError_Total",
            ),
        }

    def test_census_supportedGeographies(self):
        census = Census(2019, shouldCacheOnDisk=True)

        verifyResource("supportedGeographies.csv", exists=False)

        _ = census.getSupportedGeographies()

        inMemSupportedGeos = census.supportedGeographies

        assert inMemSupportedGeos.__dict__ == {
            "CongressionalDistrict": "congressional district",
            "County": "county",
            "Division": "division",
            "Region": "region",
            "State": "state",
            "Us": "us",
        }
        verifyResource("supportedGeographies.csv")

    def test_census_searchGroups(self):
        census = Census(2019)
        regex = r"sex by age by .* difficulty"

        res = census.searchGroups(regex)

        expectedRes = [
            {
                "code": "B18104",
                "description": "SEX BY AGE BY COGNITIVE DIFFICULTY",
            },
            {
                "code": "B18105",
                "description": "SEX BY AGE BY AMBULATORY DIFFICULTY",
            },
        ]

        assert res.to_dict("records") == expectedRes

    def test_census_searchVariablesWithinGroups(self, apiCalls: Set[str]):
        census = Census(2019)
        regex = r"estimate"

        res = census.searchVariables(regex, GroupCode("B18104"), GroupCode("B18105"))

        expectedRes = [
            {
                "code": "B18104_001E",
                "groupCode": "B18104",
                "groupConcept": "SEX BY AGE BY COGNITIVE DIFFICULTY",
                "limit": 0,
                "name": "Estimate!!Total:",
                "predicateOnly": True,
                "predicateType": "int",
            },
            {
                "code": "B18104_001EA",
                "groupCode": "B18104",
                "groupConcept": "SEX BY AGE BY COGNITIVE DIFFICULTY",
                "limit": 0,
                "name": "Annotation of Estimate!!Total:",
                "predicateOnly": True,
                "predicateType": "string",
            },
            {
                "code": "B18105_001E",
                "groupCode": "B18105",
                "groupConcept": "SEX BY AGE BY AMBULATORY DIFFICULTY",
                "limit": 0,
                "name": "Estimate!!Total:",
                "predicateOnly": True,
                "predicateType": "int",
            },
            {
                "code": "B18105_001EA",
                "groupCode": "B18105",
                "groupConcept": "SEX BY AGE BY AMBULATORY DIFFICULTY",
                "limit": 0,
                "name": "Annotation of Estimate!!Total:",
                "predicateOnly": True,
                "predicateType": "string",
            },
        ]

        assert {
            "https://api.census.gov/data/2019/acs/acs1/groups/B18105.json",
            "https://api.census.gov/data/2019/acs/acs1/groups/B18104.json",
        }.issubset(apiCalls)
        assert res.to_dict("records") == expectedRes

    def test_census_searchAllVariables(self, apiCalls: Set[str]):
        census = Census(2019)
        regex = r"estimate"

        res = census.searchVariables(regex)

        expectedRes = [
            {
                "code": "B17015_001E",
                "groupCode": "B17015",
                "groupConcept": "POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY "
                "TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY "
                "INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                "limit": 0,
                "name": "Estimate!!Total:",
                "predicateOnly": True,
                "predicateType": "int",
            },
            {
                "code": "B17015_001EA",
                "groupCode": "B17015",
                "groupConcept": "POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY "
                "TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY "
                "INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                "limit": 0,
                "name": "Annotation of Estimate!!Total:",
                "predicateOnly": True,
                "predicateType": "string",
            },
            {
                "code": "B18104_001E",
                "groupCode": "B18104",
                "groupConcept": "SEX BY AGE BY COGNITIVE DIFFICULTY",
                "limit": 0,
                "name": "Estimate!!Total:",
                "predicateOnly": True,
                "predicateType": "int",
            },
            {
                "code": "B18104_001EA",
                "groupCode": "B18104",
                "groupConcept": "SEX BY AGE BY COGNITIVE DIFFICULTY",
                "limit": 0,
                "name": "Annotation of Estimate!!Total:",
                "predicateOnly": True,
                "predicateType": "string",
            },
            {
                "code": "B18105_001E",
                "groupCode": "B18105",
                "groupConcept": "SEX BY AGE BY AMBULATORY DIFFICULTY",
                "limit": 0,
                "name": "Estimate!!Total:",
                "predicateOnly": True,
                "predicateType": "int",
            },
            {
                "code": "B18105_001EA",
                "groupCode": "B18105",
                "groupConcept": "SEX BY AGE BY AMBULATORY DIFFICULTY",
                "limit": 0,
                "name": "Annotation of Estimate!!Total:",
                "predicateOnly": True,
                "predicateType": "string",
            },
        ]

        assert {
            "https://api.census.gov/data/2019/acs/acs1/variables.json",
        }.issubset(apiCalls)

        assert res.to_dict("records") == expectedRes

    @pytest.mark.parametrize("shouldRenameColumns", [(True), (False)])
    def test_census_stats_batchedApiCalls(
        self, apiCalls: Set[str], mocker: MockerFixture, shouldRenameColumns: bool
    ):
        census = Census(2019, replaceColumnHeaders=shouldRenameColumns)

        mocker.patch("the_census._api.fetch.MAX_QUERY_SIZE", 2)

        variables = [
            VariableCode(code)
            for code in "B17015_001E,B18104_001E,B18105_001E".split(",")
        ]
        forDomain = GeoDomain("congressional district")
        inDomains = [GeoDomain("state", "01")]
        _ = census.getAllVariables()

        res = census.getStats(variables, forDomain, *inDomains)

        assert res.to_dict("records") == (
            expectedStatsResWithNames
            if shouldRenameColumns
            else expectedStatsResWithoutNames
        )

        assert {
            "https://api.census.gov/data/2019/acs/acs1?get=NAME,B17015_001E&for=congressional%20district:*&in=state:01",
            "https://api.census.gov/data/2019/acs/acs1?get=NAME,B18104_001E&for=congressional%20district:*&in=state:01",
            "https://api.census.gov/data/2019/acs/acs1?get=NAME,B18105_001E&for=congressional%20district:*&in=state:01",
        }.issubset(apiCalls)

    def test_census_stats_columnNameChangeWithDuplicate(self):
        variables = [
            VariableCode(code)
            for code in "B17015_001E,B18104_001E,B18105_001E".split(",")
        ]
        forDomain = GeoDomain("congressional district")
        inDomains = [GeoDomain("state", "01")]

        census = Census(
            2019,
            replaceColumnHeaders=True,
        )

        # to populate "variables"
        _ = census.getAllVariables()

        res = census.getStats(variables, forDomain, *inDomains)

        assert res.to_dict("records") == [
            {
                "NAME": "Congressional District 1 (116th Congress), Alabama",
                "congressional district": "01",
                "state": "01",
                "Estimate_Total_B17015": 172441,
                "Estimate_Total_B18104": 664816,
                "Estimate_Total_B18105": 664816,
            },
            {
                "NAME": "Congressional District 2 (116th Congress), Alabama",
                "congressional district": "02",
                "state": "01",
                "Estimate_Total_B17015": 168129,
                "Estimate_Total_B18104": 610312,
                "Estimate_Total_B18105": 610312,
            },
            {
                "NAME": "Congressional District 3 (116th Congress), Alabama",
                "congressional district": "03",
                "state": "01",
                "Estimate_Total_B17015": 184320,
                "Estimate_Total_B18104": 664930,
                "Estimate_Total_B18105": 664930,
            },
            {
                "NAME": "Congressional District 4 (116th Congress), Alabama",
                "congressional district": "04",
                "state": "01",
                "Estimate_Total_B17015": 179508,
                "Estimate_Total_B18104": 640347,
                "Estimate_Total_B18105": 640347,
            },
            {
                "NAME": "Congressional District 5 (116th Congress), Alabama",
                "congressional district": "05",
                "state": "01",
                "Estimate_Total_B17015": 195668,
                "Estimate_Total_B18104": 681411,
                "Estimate_Total_B18105": 681411,
            },
            {
                "NAME": "Congressional District 6 (116th Congress), Alabama",
                "congressional district": "06",
                "state": "01",
                "Estimate_Total_B17015": 186592,
                "Estimate_Total_B18104": 653559,
                "Estimate_Total_B18105": 653559,
            },
            {
                "NAME": "Congressional District 7 (116th Congress), Alabama",
                "congressional district": "07",
                "state": "01",
                "Estimate_Total_B17015": 151225,
                "Estimate_Total_B18104": 620542,
                "Estimate_Total_B18105": 620542,
            },
        ]

    def test_census_stats_columnNameChangeWithoutDuplicate(self):
        variables = [VariableCode("B17015_001E")]
        forDomain = GeoDomain("congressional district")
        inDomains = [GeoDomain("state", "01")]

        census = Census(
            2019,
            shouldLoadFromExistingCache=True,
            shouldCacheOnDisk=True,
            replaceColumnHeaders=True,
        )

        # to populate "variables"
        _ = census.getAllVariables()

        res = census.getStats(variables, forDomain, *inDomains)

        assert res.to_dict("records") == [
            {
                "NAME": "Congressional District 1 (116th Congress), Alabama",
                "congressional district": "01",
                "state": "01",
                "Estimate_Total": 172441,
            },
            {
                "NAME": "Congressional District 2 (116th Congress), Alabama",
                "congressional district": "02",
                "state": "01",
                "Estimate_Total": 168129,
            },
            {
                "NAME": "Congressional District 3 (116th Congress), Alabama",
                "congressional district": "03",
                "state": "01",
                "Estimate_Total": 184320,
            },
            {
                "NAME": "Congressional District 4 (116th Congress), Alabama",
                "congressional district": "04",
                "state": "01",
                "Estimate_Total": 179508,
            },
            {
                "NAME": "Congressional District 5 (116th Congress), Alabama",
                "congressional district": "05",
                "state": "01",
                "Estimate_Total": 195668,
            },
            {
                "NAME": "Congressional District 6 (116th Congress), Alabama",
                "congressional district": "06",
                "state": "01",
                "Estimate_Total": 186592,
            },
            {
                "NAME": "Congressional District 7 (116th Congress), Alabama",
                "congressional district": "07",
                "state": "01",
                "Estimate_Total": 151225,
            },
        ]

    @pytest.mark.parametrize("shouldLoadFromCache", [(True), (False)])
    def test_census_givenLoadFromCache_populatesRepository(
        self,
        shouldLoadFromCache: bool,
        givenCacheWithGroup: None,
        givenCacheWithVariables: None,
    ):

        census = Census(
            2019,
            shouldLoadFromExistingCache=shouldLoadFromCache,
            shouldCacheOnDisk=True,
        )
        expectedRepoVars = VariableSet(
            GroupVariable(
                code=VariableCode("v1"),
                groupCode=GroupCode("g1"),
                groupConcept="group 1",
                name="variable 1",
                limit=0,
                predicateOnly=True,
                predicateType="int",
                cleanedName="Variable 1",
            ),
            GroupVariable(
                code=VariableCode("v2"),
                groupCode=GroupCode("g1"),
                groupConcept="group 1",
                name="variable 2",
                limit=0,
                predicateOnly=True,
                predicateType="int",
                cleanedName="Variable 2",
            ),
        )
        expectedRepoGroups = GroupSet(
            Group(GroupCode("abc"), "alphabet", cleanedName="Alphabet"),
            Group(GroupCode("123"), "numbers", cleanedName="Numbers"),
        )

        repoVars = census.variables
        repoGroups = census.groups

        if shouldLoadFromCache:
            assert repoVars == expectedRepoVars
            assert repoGroups == expectedRepoGroups
        else:
            assert len(repoVars) == 0
            assert len(repoGroups) == 0

    def test_logging(self):
        _ = Census(2019, "acs", "acs1")

        with open("census.log", "r") as f:
            print(f.read())

    def test_listAvailableDatasets(self):
        datasets = Census.listAvailabeDatasets()

        assert datasets.to_dict("records") == [
            {
                "datasetType": "ecneoyinv",
                "description": "This dataset presents statistics for Wholesale Trade:  "
                "Inventories by Valuation Method for the U.S.",
                "name": "Economic Census: Economic Census of the United States: Wholesale "
                "Trade: Inventories by Valuation Method for the U.S.",
                "surveyType": "",
                "year": 2017,
            },
            {
                "datasetType": "dec",
                "description": "Summary File 4 is repeated or iterated for the total "
                "population and 335 additional population groups: 132 race "
                "groups,78 American Indian and Alaska Native tribe categories, "
                "39 Hispanic or Latino groups, and 86 ancestry groups.Tables "
                "for any population group excluded from SF 2 because the "
                "group's total population in a specific geographic area did "
                "not meet the SF 2 threshold of 100 people are excluded from "
                "SF 4. Tables in SF 4 shown for any of the above population "
                "groups will only be shown if there are at least 50 unweighted "
                "sample cases in a specific geographic area. The same 50 "
                "unweighted sample cases also applied to ancestry iterations. "
                "In an iterated file such as SF 4, the universes households, "
                "families, and occupied housing units are classified by the "
                "race or ethnic group of the householder. The universe "
                "subfamilies is classified by the race or ethnic group of the "
                "reference person for the subfamily. In a husband/wife "
                "subfamily, the reference person is the husband; in a "
                "parent/child subfamily, the reference person is always the "
                "parent. The universes population in households, population in "
                "families, and population in subfamilies are classified by the "
                "race or ethnic group of the inidviduals within the household, "
                "family, or subfamily without regard to the race or ethnicity "
                "of the householder. Notes follow selected tables to make the "
                "classification of the universe clear. In any population table "
                "where there is no note, the universe classification is always "
                "based on the race or ethnicity of the person. In all housing "
                "tables, the universe classification is based on the race or "
                "ethnicity of the householder.",
                "name": "Decennial Census: Summary File 4",
                "surveyType": "sf4",
                "year": 2000,
            },
        ]

    def test_repr(self):
        c = Census(2019)

        assert str(c) == "<Census year=2019 dataset=acs survey=acs1>"

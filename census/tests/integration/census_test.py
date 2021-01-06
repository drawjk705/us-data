from pytest_mock.plugin import MockerFixture  # type: ignore
from census.variables.models import Group, GroupCode, GroupVariable, VariableCode
import pandas
from census.models import GeoDomain
from pathlib import Path
from census.client.census import Census
from census.getCensus import getCensus
from census.exceptions import CensusDoesNotExistException
from typing import Any, Dict, List, Optional, Set
from tests.integration.mockApiResponses import MOCK_API
import requests
from _pytest.monkeypatch import MonkeyPatch
import pytest
import os
import shutil


class _Response:
    status_code: int
    content: Any

    def __init__(self, status_code: int, content: Any) -> None:
        self.content = content
        self.status_code = status_code

    def json(self) -> Any:
        if self.status_code != 200:
            raise Exception("Uh oh")

        return self.content


expectedStatsRes = [
    {
        "NAME": "Congressional District 1 (116th Congress), Alabama",
        "state": "01",
        "congressional district": "01",
        "B17015_001E": "172441",
        "B18104_001E": "664816",
        "B18105_001E": "664816",
    },
    {
        "NAME": "Congressional District 3 (116th Congress), Alabama",
        "state": "01",
        "congressional district": "03",
        "B17015_001E": "184320",
        "B18104_001E": "664930",
        "B18105_001E": "664930",
    },
    {
        "NAME": "Congressional District 5 (116th Congress), Alabama",
        "state": "01",
        "congressional district": "05",
        "B17015_001E": "195668",
        "B18104_001E": "681411",
        "B18105_001E": "681411",
    },
    {
        "NAME": "Congressional District 4 (116th Congress), Alabama",
        "state": "01",
        "congressional district": "04",
        "B17015_001E": "179508",
        "B18104_001E": "640347",
        "B18105_001E": "640347",
    },
    {
        "NAME": "Congressional District 7 (116th Congress), Alabama",
        "state": "01",
        "congressional district": "07",
        "B17015_001E": "151225",
        "B18104_001E": "620542",
        "B18105_001E": "620542",
    },
    {
        "NAME": "Congressional District 2 (116th Congress), Alabama",
        "state": "01",
        "congressional district": "02",
        "B17015_001E": "168129",
        "B18104_001E": "610312",
        "B18105_001E": "610312",
    },
    {
        "NAME": "Congressional District 6 (116th Congress), Alabama",
        "state": "01",
        "congressional district": "06",
        "B17015_001E": "186592",
        "B18104_001E": "653559",
        "B18105_001E": "653559",
    },
]


def verifyResource(
    resource: str,
    exists: bool = True,
    expectedData: Optional[List[Dict[str, Any]]] = None,
):
    if not exists:
        assert not Path(f"cache/2019/acs/acs1/{resource}").exists()
    else:
        path = Path(f"cache/2019/acs/acs1/{resource}")
        assert path.exists()

        if expectedData:
            df = pandas.read_csv(path)  # type: ignore
            assert df.to_dict("records") == expectedData


@pytest.fixture(scope="function", autouse=True)
def apiCalls(monkeypatch: MonkeyPatch):
    _apiCalls: Set[str] = set()

    def mockGet(route: str):
        _apiCalls.add(route)
        res = MOCK_API.get(route)
        status_code = 404 if res is None else 200
        return _Response(status_code, res)

    monkeypatch.setattr(requests, "get", mockGet)

    return _apiCalls


@pytest.fixture(scope="function", autouse=True)
def setPathToTest():
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
def tempDir() -> Path:
    return Path()


@pytest.fixture
def censusNoCache() -> Census:
    return getCensus(2019, shouldCacheOnDisk=False)


@pytest.fixture
def censusCacheNoLoad() -> Census:
    return getCensus(2019, shouldCacheOnDisk=True, shouldLoadFromExistingCache=False)


@pytest.fixture
def cachedCensus() -> Census:
    return getCensus(2019, shouldCacheOnDisk=True, shouldLoadFromExistingCache=True)


@pytest.mark.integration
class TestCensus:
    def test_census_givenInvalidDataRequest(self):
        with pytest.raises(CensusDoesNotExistException, match=""):
            _ = getCensus(2020)

    def test_censusNoCache_doesNotCreateCache(
        self, censusNoCache: Census, tempDir: Path
    ):
        _ = censusNoCache.getGroups()

        assert not tempDir.joinpath("cache").exists()

    def test_censusCacheNoLoad_createsCacheButDoesNotLoadIt(
        self, censusCacheNoLoad: Census, tempDir: Path, apiCalls: Set[str]
    ):
        tempDir.joinpath("cache").mkdir(parents=True, exist_ok=True)
        pandas.DataFrame(
            [
                dict(code="abc", description="alphabet"),
                dict(code="123", description="numbers"),
            ]
        ).to_csv("./cache/2019/acs/acs1/groups.csv")
        verifyResource("groups.csv")

        _ = censusCacheNoLoad.getGroups()

        assert {"https://api.census.gov/data/2019/acs/acs1/groups.json"}.issubset(
            apiCalls
        )

        assert tempDir.joinpath("cache").exists()

    def test_cachedCensus_createsCacheAndLoadsItOnQuery(
        self, cachedCensus: Census, tempDir: Path, apiCalls: Set[str]
    ):
        tempDir.joinpath("cache").mkdir(parents=True, exist_ok=True)
        pandas.DataFrame(
            [
                dict(code="abc", description="alphabet"),
                dict(code="123", description="numbers"),
            ]
        ).to_csv("./cache/2019/acs/acs1/groups.csv")
        verifyResource("groups.csv")

        _ = cachedCensus.getGroups()

        assert "https://api.census.gov/data/2019/acs/acs1/groups.json" not in apiCalls
        assert len(apiCalls) == 1

        assert tempDir.joinpath("cache").exists()

    def test_cachedCensus_getGeographyCodes(self, cachedCensus: Census, tempDir: Path):
        codes = cachedCensus.getGeographyCodes(
            forDomain=GeoDomain("congressional district"),
            inDomains=[GeoDomain("state", "01")],
        )

        expected = [
            {
                "NAME": "Congressional District 1 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "01",
            },
            {
                "NAME": "Congressional District 3 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "03",
            },
            {
                "NAME": "Congressional District 5 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "05",
            },
            {
                "NAME": "Congressional District 4 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "04",
            },
            {
                "NAME": "Congressional District 7 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "07",
            },
            {
                "NAME": "Congressional District 2 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "02",
            },
            {
                "NAME": "Congressional District 6 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "06",
            },
        ]

        assert codes.to_dict("records") == expected

    def test_cachedCensus_groupsAndVariables(self, cachedCensus: Census):
        verifyResource("groups.csv", exists=False)
        _ = cachedCensus.getGroups()
        groupCodes = [groupCode.code for groupCode in cachedCensus.groups.values()]
        verifyResource("groups.csv")
        assert len(groupCodes) == 3

        for code in groupCodes:
            verifyResource(f"variables/{code}.csv", exists=False)
        variables = cachedCensus.getVariablesByGroup(groupCodes)
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

        assert len(cachedCensus.variables) == 12

    def test_cachedCensus_getAllVariables(self, cachedCensus: Census):
        allVars = cachedCensus.getAllVariables()

        assert len(allVars.to_dict("records")) == 12
        assert len(cachedCensus.variables) == 12

        for group, variables in allVars.groupby(["groupCode"]):  # type: ignore
            verifyResource(
                f"variables/{group}.csv",
                exists=True,
                expectedData=variables.to_dict("records"),
            )

    def test_cachedCensus_groups_populatesGroupNames(self, cachedCensus: Census):
        cachedCensus.getGroups()

        assert dict(cachedCensus.groups.items()) == {
            "PovertyStatusInThePast12MonthsOfFamiliesByFamilyTypeBySocialSecurityIncomeBySupplementalSecurityIncomeSsiAndCashPublicAssistanceIncome": Group(
                code=GroupCode("B17015"),
                description="POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
            ),
            "SexByAgeByAmbulatoryDifficulty": Group(
                code=GroupCode("B18105"),
                description="SEX BY AGE BY AMBULATORY DIFFICULTY",
            ),
            "SexByAgeByCognitiveDifficulty": Group(
                code=GroupCode("B18104"),
                description="SEX BY AGE BY COGNITIVE DIFFICULTY",
            ),
        }

    def test_cachedCensus_variables_populatesVariableNames(self, cachedCensus: Census):
        cachedCensus.getAllVariables()

        assert dict(cachedCensus.variables.items()) == {
            "AnnotationOfEstimate_Total_B17015": GroupVariable(
                code=VariableCode("B17015_001EA"),
                groupCode=GroupCode("B17015"),
                groupConcept="POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                name="Annotation of Estimate!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="string",
            ),
            "AnnotationOfEstimate_Total_B18104": GroupVariable(
                code=VariableCode("B18104_001EA"),
                groupCode=GroupCode("B18104"),
                groupConcept="SEX BY AGE BY COGNITIVE DIFFICULTY",
                name="Annotation of Estimate!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="string",
            ),
            "AnnotationOfEstimate_Total_B18105": GroupVariable(
                code=VariableCode("B18105_001EA"),
                groupCode=GroupCode("B18105"),
                groupConcept="SEX BY AGE BY AMBULATORY DIFFICULTY",
                name="Annotation of Estimate!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="string",
            ),
            "AnnotationOfMarginOfError_Total_B17015": GroupVariable(
                code=VariableCode("B17015_001MA"),
                groupCode=GroupCode("B17015"),
                groupConcept="POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                name="Annotation of Margin of Error!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="string",
            ),
            "AnnotationOfMarginOfError_Total_B18104": GroupVariable(
                code=VariableCode("B18104_001MA"),
                groupCode=GroupCode("B18104"),
                groupConcept="SEX BY AGE BY COGNITIVE DIFFICULTY",
                name="Annotation of Margin of Error!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="string",
            ),
            "AnnotationOfMarginOfError_Total_B18105": GroupVariable(
                code=VariableCode("B18105_001MA"),
                groupCode=GroupCode("B18105"),
                groupConcept="SEX BY AGE BY AMBULATORY DIFFICULTY",
                name="Annotation of Margin of Error!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="string",
            ),
            "Estimate_Total_B17015": GroupVariable(
                code=VariableCode("B17015_001E"),
                groupCode=GroupCode("B17015"),
                groupConcept="POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                name="Estimate!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="int",
            ),
            "Estimate_Total_B18104": GroupVariable(
                code=VariableCode("B18104_001E"),
                groupCode=GroupCode("B18104"),
                groupConcept="SEX BY AGE BY COGNITIVE DIFFICULTY",
                name="Estimate!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="int",
            ),
            "Estimate_Total_B18105": GroupVariable(
                code=VariableCode("B18105_001E"),
                groupCode=GroupCode("B18105"),
                groupConcept="SEX BY AGE BY AMBULATORY DIFFICULTY",
                name="Estimate!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="int",
            ),
            "MarginOfError_Total_B17015": GroupVariable(
                code=VariableCode("B17015_001M"),
                groupCode=GroupCode("B17015"),
                groupConcept="POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                name="Margin of Error!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="int",
            ),
            "MarginOfError_Total_B18104": GroupVariable(
                code=VariableCode("B18104_001M"),
                groupCode=GroupCode("B18104"),
                groupConcept="SEX BY AGE BY COGNITIVE DIFFICULTY",
                name="Margin of Error!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="int",
            ),
            "MarginOfError_Total_B18105": GroupVariable(
                code=VariableCode("B18105_001M"),
                groupCode=GroupCode("B18105"),
                groupConcept="SEX BY AGE BY AMBULATORY DIFFICULTY",
                name="Margin of Error!!Total:",
                limit=0,
                predicateOnly=True,
                predicateType="int",
            ),
        }

    def test_cachedCensus_supportedGeographies(self, cachedCensus: Census):
        verifyResource("supportedGeographies.csv", exists=False)

        _ = cachedCensus.getSupportedGeographies()

        verifyResource("supportedGeographies.csv")

    def test_cachedCensus_searchGroups(self, cachedCensus: Census):
        regex = r"sex by age by .* difficulty"

        res = cachedCensus.searchGroups(regex)

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

    def test_cachedCensus_searchVariablesWithinGroups(
        self, cachedCensus: Census, apiCalls: Set[str]
    ):
        regex = r"estimate"

        res = cachedCensus.searchVariables(
            regex, "name", inGroups=[GroupCode("B18104"), GroupCode("B18105")]
        )

        expectedRes = [
            {
                "code": "B18104_001E",
                "groupCode": "B18104",
                "groupConcept": "SEX BY AGE BY COGNITIVE DIFFICULTY",
                "name": "Estimate!!Total:",
                "predicateType": "int",
                "limit": 0,
                "predicateOnly": True,
            },
            {
                "code": "B18104_001EA",
                "groupCode": "B18104",
                "groupConcept": "SEX BY AGE BY COGNITIVE DIFFICULTY",
                "name": "Annotation of Estimate!!Total:",
                "predicateType": "string",
                "limit": 0,
                "predicateOnly": True,
            },
            {
                "code": "B18105_001E",
                "groupCode": "B18105",
                "groupConcept": "SEX BY AGE BY AMBULATORY DIFFICULTY",
                "name": "Estimate!!Total:",
                "predicateType": "int",
                "limit": 0,
                "predicateOnly": True,
            },
            {
                "code": "B18105_001EA",
                "groupCode": "B18105",
                "groupConcept": "SEX BY AGE BY AMBULATORY DIFFICULTY",
                "name": "Annotation of Estimate!!Total:",
                "predicateType": "string",
                "limit": 0,
                "predicateOnly": True,
            },
        ]

        assert {
            "https://api.census.gov/data/2019/acs/acs1/groups/B18105.json",
            "https://api.census.gov/data/2019/acs/acs1/groups/B18104.json",
        }.issubset(apiCalls)
        assert res.to_dict("records") == expectedRes

    def test_cachedCensus_searchAllVariables(
        self, cachedCensus: Census, apiCalls: Set[str]
    ):
        regex = r"estimate"

        res = cachedCensus.searchVariables(regex, "name", inGroups=[])

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

    def test_cachedCensus_stats_batchedApiCalls(
        self, cachedCensus: Census, apiCalls: Set[str], mocker: MockerFixture
    ):
        mocker.patch("census.api.fetch.MAX_QUERY_SIZE", 2)

        variables = [
            VariableCode(code)
            for code in "B17015_001E,B18104_001E,B18105_001E".split(",")
        ]
        forDomain = GeoDomain("congressional district")
        inDomains = [GeoDomain("state", "01")]

        res = cachedCensus.getStats(variables, forDomain, inDomains)

        assert res.to_dict("records") == expectedStatsRes

        assert {
            "https://api.census.gov/data/2019/acs/acs1?get=NAME,B17015_001E&for=congressional%20district:*&in=state:01",
            "https://api.census.gov/data/2019/acs/acs1?get=NAME,B18104_001E&for=congressional%20district:*&in=state:01",
            "https://api.census.gov/data/2019/acs/acs1?get=NAME,B18105_001E&for=congressional%20district:*&in=state:01",
        }.issubset(apiCalls)

    def test_cachedCensus_stats_noColumnNameChange(
        self, cachedCensus: Census, apiCalls: Set[str]
    ):
        variables = [
            VariableCode(code)
            for code in "B17015_001E,B18104_001E,B18105_001E".split(",")
        ]
        forDomain = GeoDomain("congressional district")
        inDomains = [GeoDomain("state", "01")]

        res = cachedCensus.getStats(variables, forDomain, inDomains)

        assert res.to_dict("records") == expectedStatsRes
        assert (
            "https://api.census.gov/data/2019/acs/acs1?get=NAME,B17015_001E,B18104_001E,B18105_001E&for=congressional%20district:*&in=state:01"
            in apiCalls
        )

    def test_cachedCensus_stats_columnNameChangeWithDuplicate(
        self, cachedCensus: Census
    ):
        variables = [
            VariableCode(code)
            for code in "B17015_001E,B18104_001E,B18105_001E".split(",")
        ]
        forDomain = GeoDomain("congressional district")
        inDomains = [GeoDomain("state", "01")]

        # to populate "variables"
        _ = cachedCensus.getAllVariables()

        res = cachedCensus.getStats(
            variables, forDomain, inDomains, replaceColumnHeaders=True
        )

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
                "NAME": "Congressional District 3 (116th Congress), Alabama",
                "congressional district": "03",
                "state": "01",
                "Estimate_Total_B17015": 184320,
                "Estimate_Total_B18104": 664930,
                "Estimate_Total_B18105": 664930,
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
                "NAME": "Congressional District 4 (116th Congress), Alabama",
                "congressional district": "04",
                "state": "01",
                "Estimate_Total_B17015": 179508,
                "Estimate_Total_B18104": 640347,
                "Estimate_Total_B18105": 640347,
            },
            {
                "NAME": "Congressional District 7 (116th Congress), Alabama",
                "congressional district": "07",
                "state": "01",
                "Estimate_Total_B17015": 151225,
                "Estimate_Total_B18104": 620542,
                "Estimate_Total_B18105": 620542,
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
                "NAME": "Congressional District 6 (116th Congress), Alabama",
                "congressional district": "06",
                "state": "01",
                "Estimate_Total_B17015": 186592,
                "Estimate_Total_B18104": 653559,
                "Estimate_Total_B18105": 653559,
            },
        ]

    def test_cachedCensus_stats_columnNameChangeWithoutDuplicate(
        self, cachedCensus: Census
    ):
        variables = [VariableCode("B17015_001E")]
        forDomain = GeoDomain("congressional district")
        inDomains = [GeoDomain("state", "01")]

        # to populate "variables"
        _ = cachedCensus.getAllVariables()

        res = cachedCensus.getStats(
            variables, forDomain, inDomains, replaceColumnHeaders=True
        )

        assert res.to_dict("records") == [
            {
                "NAME": "Congressional District 1 (116th Congress), Alabama",
                "congressional district": "01",
                "state": "01",
                "Estimate_Total": 172441,
            },
            {
                "NAME": "Congressional District 3 (116th Congress), Alabama",
                "congressional district": "03",
                "state": "01",
                "Estimate_Total": 184320,
            },
            {
                "NAME": "Congressional District 5 (116th Congress), Alabama",
                "congressional district": "05",
                "state": "01",
                "Estimate_Total": 195668,
            },
            {
                "NAME": "Congressional District 4 (116th Congress), Alabama",
                "congressional district": "04",
                "state": "01",
                "Estimate_Total": 179508,
            },
            {
                "NAME": "Congressional District 7 (116th Congress), Alabama",
                "congressional district": "07",
                "state": "01",
                "Estimate_Total": 151225,
            },
            {
                "NAME": "Congressional District 2 (116th Congress), Alabama",
                "congressional district": "02",
                "state": "01",
                "Estimate_Total": 168129,
            },
            {
                "NAME": "Congressional District 6 (116th Congress), Alabama",
                "congressional district": "06",
                "state": "01",
                "Estimate_Total": 186592,
            },
        ]

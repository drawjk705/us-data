from callee.base import Matcher
from callee.types import InstanceOf, IsA
from census.variables.models import Group, GroupCode, GroupVariable, VariableCode
from census.models import GeoDomain
from typing import Any, Dict, List, cast

from census.variables.repository.service import VariableRepository

from tests.serviceTestFixtures import ServiceTestFixture
import pandas
import pytest
from unittest.mock import MagicMock, call

# pyright: reportPrivateUsage = false


apiRetval = "banana"


class TestVariableStorageService(ServiceTestFixture[VariableRepository]):
    @pytest.mark.parametrize("isCacheHit", (True, False))
    def test_getGroups_givenCacheRetval(self, isCacheHit: bool):
        fullDf = pandas.DataFrame(
            [
                Group(GroupCode("1"), "desc1").__dict__,
                Group(GroupCode("2"), "desc2").__dict__,
            ]
        )

        self.mocker.patch.object(
            self._service._cache, "get", return_value=fullDf if isCacheHit else None
        )

        apiFetch = self.mocker.patch.object(
            self._service._api, "groupData", return_value=apiRetval
        )

        transform = self.mocker.patch.object(
            self._service._transformer, "groups", return_value=fullDf
        )

        self._service.getGroups()

        if isCacheHit:
            apiFetch.assert_not_called()
            transform.assert_not_called()
            self.castMock(self._service._cache.put).assert_not_called()
        else:
            apiFetch.assert_called_once()
            transform.assert_called_once_with(apiRetval)
            self.castMock(self._service._cache.put).assert_called_once_with(
                "groups.csv", fullDf
            )

    @pytest.mark.parametrize("isCacheHit", (True, False))
    def test_getSupportedGeographies(self, isCacheHit: bool):
        fullDf = pandas.DataFrame(
            [
                {"name": "us", "hierarchy": 1, "for": "this", "in": "that"},
                {"name": "them", "hierarchy": 2, "for": "that", "in": "this"},
            ]
        )

        self.mocker.patch.object(
            self._service._cache, "get", return_value=fullDf if isCacheHit else None
        )
        apiFetch = self.mocker.patch.object(
            self._service._api, "supportedGeographies", return_value=apiRetval
        )

        transform = self.mocker.patch.object(
            self._service._transformer, "supportedGeographies", return_value=fullDf
        )

        self._service.getSupportedGeographies()

        if isCacheHit:
            apiFetch.assert_not_called()
            transform.assert_not_called()
            self.castMock(self._service._cache.put).assert_not_called()
        else:
            apiFetch.assert_called_once()
            transform.assert_called_once_with(apiRetval)
            self.castMock(self._service._cache.put).assert_called_once_with(
                "supportedGeographies.csv", fullDf
            )

    def test_getGeographyCodes(self):
        forDomain = MagicMock()
        inDomains = [MagicMock()]

        fullDf = pandas.DataFrame(
            [
                {
                    "name": "banana",
                    "state": "01",
                },
                {
                    "name": "apple",
                    "state": "01",
                },
            ]
        )

        apiFetch = self.mocker.patch.object(
            self._service._api, "geographyCodes", return_value=apiRetval
        )
        transform = self.mocker.patch.object(
            self._service._transformer, "geographyCodes", return_value=fullDf
        )

        res = self._service.getGeographyCodes(
            forDomain, cast(List[GeoDomain], inDomains)
        )

        apiFetch.assert_called_once_with(forDomain, inDomains)
        transform.assert_called_once_with(apiRetval)

        assert res.to_dict() == fullDf.to_dict()

    def test_getVariablesByGroup(self):
        cacheHitGroup = GroupCode("hit")
        cacheMissGroup = GroupCode("miss")

        variables = pandas.DataFrame(
            [
                dict(
                    code=VariableCode("1"),
                    groupCode=GroupCode("G1"),
                    groupConcept="fruit",
                    limit=0,
                    name="variable 1",
                    predicateOnly=False,
                    predicateType="int",
                ),
                dict(
                    code=VariableCode("2"),
                    groupCode=GroupCode("G1"),
                    groupConcept="fruit",
                    limit=0,
                    name="variable 2",
                    predicateOnly=False,
                    predicateType="int",
                ),
            ]
        )

        transformer = self.castMock(self._service._transformer)
        cache = self.castMock(self._service._cache)

        self.mocker.patch.object(transformer, "variables", return_value=variables)

        def cacheGetSideEffect(resource: str) -> pandas.DataFrame:
            return variables if cacheHitGroup in resource else pandas.DataFrame()

        self.mocker.patch.object(cache, "get", side_effect=cacheGetSideEffect)

        self._service.getVariablesByGroup([cacheHitGroup, cacheMissGroup])

    def test_getAllVariables(self):
        group1Vars: List[Dict[str, Any]] = [
            dict(
                code="var1",
                groupCode="group1",
                groupConcept="concept1",
                name="name1",
                limit=1,
                predicateOnly=False,
                predicateType="string",
            ),
            dict(
                code="var2",
                groupCode="group1",
                groupConcept="concept1",
                name="name2",
                limit=1,
                predicateOnly=False,
                predicateType="string",
            ),
        ]
        group2Vars: List[Dict[str, Any]] = [
            dict(
                code="var3",
                groupCode="group2",
                groupConcept="concept2",
                name="name3",
                limit=1,
                predicateOnly=False,
                predicateType="string",
            ),
            dict(
                code="var4",
                groupCode="group2",
                groupConcept="concept2",
                name="name4",
                limit=1,
                predicateOnly=False,
                predicateType="string",
            ),
        ]
        group3Vars: List[Dict[str, Any]] = [
            dict(
                code="var5",
                groupCode="group3",
                groupConcept="concept3",
                name="name5",
                limit=1,
                predicateOnly=False,
                predicateType="string",
            ),
        ]

        def cachePutSideEffect(resource: str, _: Any) -> bool:
            return "group2" in resource or "group1" in resource

        cachePut = self.mocker.patch.object(
            self._service._cache, "put", side_effect=cachePutSideEffect
        )

        transformerRes = pandas.DataFrame(group1Vars + group2Vars + group3Vars)
        self.mocker.patch.object(
            self._service._transformer, "variables", return_value=transformerRes
        )
        expectedVariables = dict(
            var1=GroupVariable(**group1Vars[0]),
            var2=GroupVariable(**group1Vars[1]),
            var3=GroupVariable(**group2Vars[0]),
            var4=GroupVariable(**group2Vars[1]),
        )

        res = self._service.getAllVariables()

        assert res.to_dict() == transformerRes.to_dict()
        assert self._service.variables == expectedVariables

        cachePut.call_args_list == [
            call("variables/group1.csv", DataFrameMatcher(["var1", "var2"], "code")),
            call("variables/group2.csv", DataFrameMatcher(["var3", "var4"], "code")),
            call("variables/group3.csv", DataFrameMatcher(["var5"], "code")),
        ]


class DataFrameMatcher(Matcher):
    _columnsValues: List[str]
    _columnToMatch: str

    def __init__(self, columnsValues: List[str], columnToMatch: str) -> None:
        self._columnsValues = columnsValues
        self._columnToMatch = columnToMatch

    def match(self, df: Any):
        if not isinstance(df, pandas.DataFrame):
            return False
        values = df[self._columnToMatch].tolist()  # type: ignore
        return self._columnsValues == values
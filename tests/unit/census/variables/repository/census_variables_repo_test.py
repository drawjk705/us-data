from typing import Any, Dict, List, Union
from unittest.mock import call

import pandas
import pytest

from tests.serviceTestFixtures import ServiceTestFixture
from tests.utils import DataFrameColumnMatcher, shuffledCases
from us_data.census._variables.models import (
    Group,
    GroupCode,
    GroupVariable,
    VariableCode,
)
from us_data.census._variables.repository.service import VariableRepository

# pyright: reportPrivateUsage = false


apiRetval = "banana"


class TestVariableRepository(ServiceTestFixture[VariableRepository]):
    @pytest.mark.parametrize(*shuffledCases(isCacheHit=[True, False]))
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

    @pytest.mark.parametrize(*shuffledCases(cacheMissIndex=[0, 1, 2]))
    def test_getVariablesByGroup(self, cacheMissIndex: int):
        cacheGroups = [GroupCode("g1"), GroupCode("g2"), GroupCode("g3")]
        cacheMissGroup = cacheGroups[cacheMissIndex]

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
                    cleanedName="variable1",
                ),
                dict(
                    code=VariableCode("2"),
                    groupCode=GroupCode("G1"),
                    groupConcept="fruit",
                    limit=0,
                    name="variable 2",
                    predicateOnly=False,
                    predicateType="int",
                    cleanedName="variable2",
                ),
            ]
        )

        transformer = self.castMock(self._service._transformer)
        cache = self.castMock(self._service._cache)

        self.mocker.patch.object(transformer, "variables", return_value=variables)

        def cacheGetSideEffect(resource: str) -> Union[pandas.DataFrame, None]:
            return None if cacheMissGroup in resource else variables

        self.mocker.patch.object(cache, "get", side_effect=cacheGetSideEffect)

        self._service.getVariablesByGroup(*cacheGroups)

    def test_getAllVariables(self):
        group1Vars: List[Dict[str, Any]] = [
            dict(
                code="var1",
                groupCode="group1",
                groupConcept="concept1",
                name="name1",
                limit=0,
                predicateType="int",
                predicateOnly=False,
                cleanedName="Name1",
            ),
            dict(
                code="var2",
                groupCode="group1",
                groupConcept="concept1",
                name="name2",
                limit=0,
                predicateType="int",
                predicateOnly=False,
                cleanedName="Name2",
            ),
        ]
        group2Vars: List[Dict[str, Any]] = [
            dict(
                code="var3",
                groupCode="group2",
                groupConcept="concept2",
                name="name3",
                limit=0,
                predicateType="int",
                predicateOnly=False,
                cleanedName="Name3",
            ),
            dict(
                code="var4",
                groupCode="group2",
                groupConcept="concept2",
                name="name4",
                limit=0,
                predicateType="int",
                predicateOnly=False,
                cleanedName="Name4",
            ),
        ]
        group3Vars: List[Dict[str, Any]] = [
            dict(
                code="var5",
                groupCode="group3",
                groupConcept="concept3",
                name="name5",
                limit=0,
                predicateType="int",
                predicateOnly=False,
                cleanedName="Name5",
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
        expectedVariables: Dict[str, GroupVariable] = dict(
            Name1_group1=GroupVariable(**group1Vars[0]),
            Name2_group1=GroupVariable(**group1Vars[1]),
            Name3_group2=GroupVariable(**group2Vars[0]),
            Name4_group2=GroupVariable(**group2Vars[1]),
        )

        res = self._service.getAllVariables()

        assert res.to_dict() == transformerRes.drop(columns=["cleanedName"]).to_dict()  # type: ignore
        assert dict(self._service.variables.items()) == expectedVariables

        cachePut.call_args_list == [
            call(
                "variables/group1.csv", DataFrameColumnMatcher(["var1", "var2"], "code")
            ),
            call(
                "variables/group2.csv", DataFrameColumnMatcher(["var3", "var4"], "code")
            ),
            call("variables/group3.csv", DataFrameColumnMatcher(["var5"], "code")),
        ]

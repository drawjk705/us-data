from typing import Any, Dict, List, Union
from unittest.mock import call

import pandas
import pytest

from tests.serviceTestFixtures import ServiceTestFixture
from tests.utils import DataFrameColumnMatcher, shuffled_cases
from the_census._variables.models import Group, GroupCode, GroupVariable, VariableCode
from the_census._variables.repository.service import VariableRepository

# pyright: reportPrivateUsage = false


apiRetval = "banana"


class TestVariableRepository(ServiceTestFixture[VariableRepository]):
    @pytest.mark.parametrize(*shuffled_cases(isCacheHit=[True, False]))
    def test_get_groups_givenCacheRetval(self, isCacheHit: bool):
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
            self._service._api, "group_data", return_value=apiRetval
        )

        transform = self.mocker.patch.object(
            self._service._transformer, "groups", return_value=fullDf
        )

        self._service.get_groups()

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

    @pytest.mark.parametrize(*shuffled_cases(cache_miss_index=[0, 1, 2]))
    def test_get_variables_by_group(self, cache_miss_index: int):
        cacheGroups = [GroupCode("g1"), GroupCode("g2"), GroupCode("g3")]
        cache_miss_group = cacheGroups[cache_miss_index]

        variables = pandas.DataFrame(
            [
                dict(
                    code=VariableCode("1"),
                    group_code=GroupCode("G1"),
                    group_concept="fruit",
                    limit=0,
                    name="variable 1",
                    predicate_only=False,
                    predicate_type="int",
                    cleaned_name="variable1",
                ),
                dict(
                    code=VariableCode("2"),
                    group_code=GroupCode("G1"),
                    group_concept="fruit",
                    limit=0,
                    name="variable 2",
                    predicate_only=False,
                    predicate_type="int",
                    cleaned_name="variable2",
                ),
            ]
        )

        transformer = self.castMock(self._service._transformer)
        cache = self.castMock(self._service._cache)

        self.mocker.patch.object(transformer, "variables", return_value=variables)

        def cacheGetSideEffect(resource: str) -> Union[pandas.DataFrame, None]:
            return None if cache_miss_group in resource else variables

        self.mocker.patch.object(cache, "get", side_effect=cacheGetSideEffect)

        self._service.get_variables_by_group(*cacheGroups)

    def test_get_all_variables(self):
        group1Vars: List[Dict[str, Any]] = [
            dict(
                code="var1",
                group_code="group1",
                group_concept="concept1",
                name="name1",
                limit=0,
                predicate_type="int",
                predicate_only=False,
                cleaned_name="Name1",
            ),
            dict(
                code="var2",
                group_code="group1",
                group_concept="concept1",
                name="name2",
                limit=0,
                predicate_type="int",
                predicate_only=False,
                cleaned_name="Name2",
            ),
        ]
        group2Vars: List[Dict[str, Any]] = [
            dict(
                code="var3",
                group_code="group2",
                group_concept="concept2",
                name="name3",
                limit=0,
                predicate_type="int",
                predicate_only=False,
                cleaned_name="Name3",
            ),
            dict(
                code="var4",
                group_code="group2",
                group_concept="concept2",
                name="name4",
                limit=0,
                predicate_type="int",
                predicate_only=False,
                cleaned_name="Name4",
            ),
        ]
        group3Vars: List[Dict[str, Any]] = [
            dict(
                code="var5",
                group_code="group3",
                group_concept="concept3",
                name="name5",
                limit=0,
                predicate_type="int",
                predicate_only=False,
                cleaned_name="Name5",
            ),
        ]

        def cachePutSideEffect(resource: str, _: Any) -> bool:
            return "group2" in resource or "group1" in resource

        self.mocker.patch.object(
            self._service._api, "all_variables", return_value=["something"]
        )
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

        res = self._service.get_all_variables()

        assert res.to_dict() == transformerRes.drop(columns=["cleaned_name"]).to_dict()  # type: ignore
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

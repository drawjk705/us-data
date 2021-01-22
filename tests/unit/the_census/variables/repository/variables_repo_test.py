from typing import Any, Dict, List
from unittest.mock import call

import pandas
import pytest
from callee.strings import Glob, String

from tests.service_test_fixtures import ServiceTestFixture
from tests.utils import DataFrameColumnMatcher, shuffled_cases
from the_census._variables.models import Group, GroupCode, GroupVariable
from the_census._variables.repository.service import VariableRepository

# pyright: reportPrivateUsage = false


api_retval = "banana"

groups_in_cache = pandas.DataFrame(
    [
        Group(GroupCode("1"), "desc1").__dict__,
        Group(GroupCode("2"), "desc2").__dict__,
    ]
)

group1_vars: List[Dict[str, Any]] = [
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
group2_vars: List[Dict[str, Any]] = [
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
group3_vars: List[Dict[str, Any]] = [
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


class TestVariableRepository(ServiceTestFixture[VariableRepository]):
    @pytest.mark.parametrize(*shuffled_cases(is_cache_hit=[True, False]))
    def test_get_groups_given_cache_retval(self, is_cache_hit: bool):
        self.mocker.patch.object(
            self._service._cache,
            "get",
            return_value=groups_in_cache if is_cache_hit else None,
        )
        api_fetch = self.mocker.patch.object(
            self._service._api, "group_data", return_value=api_retval
        )
        transform = self.mocker.patch.object(
            self._service._transformer, "groups", return_value=groups_in_cache
        )

        self._service.get_groups()

        if is_cache_hit:
            api_fetch.assert_not_called()
            transform.assert_not_called()
            self.mocker.patch.object(self._service._cache, "put").assert_not_called()
        else:
            api_fetch.assert_called_once()
            transform.assert_called_once_with(api_retval)
            self.cast_mock(self._service._cache.put).assert_called_once_with(
                "groups.csv", groups_in_cache
            )

    @pytest.mark.parametrize(*shuffled_cases(cache_miss_index=[0, 1, 2]))
    def test_get_variables_by_group(self, cache_miss_index: int):
        cache_groups = [GroupCode("g1"), GroupCode("g2"), GroupCode("g3")]
        all_variables = [group1_vars, group2_vars, group3_vars]

        cache_miss_group = cache_groups[cache_miss_index]
        transformer_retval = pandas.DataFrame(all_variables[cache_miss_index])

        cache_side_effect = [
            pandas.DataFrame(variables) if i != cache_miss_index else None
            for i, variables in enumerate(all_variables)
        ]

        self.mocker.patch.object(
            self._service._cache, "get", side_effect=cache_side_effect
        )
        api_mock = self.mocker.patch.object(
            self._service._api, "variables_for_group", return_value="something"
        )
        self.mocker.patch.object(
            self._service._transformer, "variables", return_value=transformer_retval
        )
        expected_codes = ["var1", "var2", "var3", "var4", "var5"]

        res = self._service.get_variables_by_group(*cache_groups)

        assert res["code"].tolist() == expected_codes
        api_mock.assert_called_once_with(cache_miss_group)
        self.cast_mock(self._service._cache.put).assert_called_once_with(
            String() & Glob(f"**{cache_miss_group}**"), transformer_retval
        )

    def test_get_all_variables(self):
        def cachePutSideEffect(resource: str, _: Any) -> bool:
            return "group2" in resource or "group1" in resource

        self.mocker.patch.object(
            self._service._api, "all_variables", return_value=["something"]
        )
        cache_put = self.mocker.patch.object(
            self._service._cache, "put", side_effect=cachePutSideEffect
        )

        transformer_res = pandas.DataFrame(group1_vars + group2_vars + group3_vars)
        self.mocker.patch.object(
            self._service._transformer, "variables", return_value=transformer_res
        )
        expectedVariables: Dict[str, GroupVariable] = dict(
            Name1_group1=GroupVariable(**group1_vars[0]),
            Name2_group1=GroupVariable(**group1_vars[1]),
            Name3_group2=GroupVariable(**group2_vars[0]),
            Name4_group2=GroupVariable(**group2_vars[1]),
        )

        res = self._service.get_all_variables()

        assert res.to_dict() == transformer_res.drop(columns=["cleaned_name"]).to_dict()  # type: ignore
        assert dict(self._service.variables.items()) == expectedVariables

        cache_put.call_args_list == [
            call(
                "variables/group1.csv", DataFrameColumnMatcher(["var1", "var2"], "code")
            ),
            call(
                "variables/group2.csv", DataFrameColumnMatcher(["var3", "var4"], "code")
            ),
            call("variables/group3.csv", DataFrameColumnMatcher(["var5"], "code")),
        ]

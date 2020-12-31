from typing import Optional

import hypothesis
from census.api.fetch import ApiFetchService
from census.dataTransformation.IDataTransformer import IDataTransformer
from census.variableRetrieval.ICache import ICache
from census.variableRetrieval.variablesToDataFrame import VariablesToDataFrameService
import pytest
from unittest.mock import MagicMock

mockCache: MagicMock
mockTransformer: MagicMock
mockApi: MagicMock

# pyright: reportPrivateUsage = false


@pytest.fixture(autouse=True)
def setup():
    global mockCache, mockTransformer, mockApi
    mockCache = MagicMock(ICache)
    mockTransformer = MagicMock(IDataTransformer)
    mockApi = MagicMock(ApiFetchService)


@pytest.fixture
def service() -> VariablesToDataFrameService:
    return VariablesToDataFrameService(
        cache=mockCache, transformer=mockTransformer, api=mockApi
    )


from pytest_mock.plugin import MockerFixture


class MockDf:
    empty: bool

    def __init__(self, empty: bool) -> None:
        self.empty = empty


@pytest.mark.parametrize("isCacheHit", [True, False])
def test_getGroups_givenCacheRetval_makesCalls(
    service: VariablesToDataFrameService,
    mocker: MockerFixture,
    isCacheHit: bool,
):
    cacheRetval = MockDf(empty=not isCacheHit)

    mocker.patch.object(service, "_populateCodes")
    mocker.patch.object(mockCache, "get", return_value=cacheRetval)

    apiRetval = "banana"
    transformerRetval = "apple"

    mocker.patch.object(mockTransformer, "groups", return_value=transformerRetval)
    mocker.patch.object(mockApi, "groupData", return_value=apiRetval)

    service.getGroups()

    if isCacheHit:
        mockApi.groupData.assert_not_called()
        mockTransformer.groups.assert_not_called()
        mockCache.put.assert_not_called()
        service._populateCodes.assert_called_once_with(
            cacheRetval, service.groupCodes, "description"
        )
    else:
        mockApi.groupData.assert_called_once()
        mockTransformer.groups.assert_called_once_with(apiRetval)
        mockCache.put.assert_called_once_with("groups.csv", transformerRetval)
        service._populateCodes.assert_called_once_with(
            transformerRetval, service.groupCodes, "description"
        )

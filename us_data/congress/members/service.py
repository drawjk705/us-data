from functools import cache
from typing import List, cast

import pandas as pd

from us_data.congress.api.interface import ICongressApiFetchService
from us_data.congress.api.models import Congressman
from us_data.congress.members.interface import ICongressMemberRepository
from us_data.congress.transformation.interface import ICongressDataTransformationService


class CongressMemberRepository(ICongressMemberRepository):
    _api: ICongressApiFetchService
    _transformer: ICongressDataTransformationService

    def __init__(
        self,
        api: ICongressApiFetchService,
        transformer: ICongressDataTransformationService,
    ) -> None:
        self._api = api
        self._transformer = transformer

    def getRepresentatives(self) -> pd.DataFrame:
        return self.__getRepresentatives()

    @cache
    def __getRepresentatives(self) -> pd.DataFrame:
        apiRes = cast(List[Congressman], self._api.getRepresentatives())

        return self._transformer.congressmembers(apiRes)

    def getSenators(self) -> pd.DataFrame:
        return self.__getSenators()

    @cache
    def __getSenators(self) -> pd.DataFrame:
        apiRes = cast(List[Congressman], self._api.getSenators())

        return self._transformer.congressmembers(apiRes)

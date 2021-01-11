from functools import cache
from congress.api.models import Congressman
from typing import List, cast
from congress.transformation.interface import ICongressTransformationService
from congress.api.interface import ICongressApiFetchService
import pandas as pd
from congress.members.interface import ICongressMemberRepository


class CongressMemberRepository(ICongressMemberRepository):
    _api: ICongressApiFetchService
    _transformer: ICongressTransformationService

    def __init__(
        self,
        api: ICongressApiFetchService,
        transformer: ICongressTransformationService,
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
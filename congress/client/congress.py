import pandas as pd

from congress.members.interface import ICongressMemberRepository


class Congress:
    """
    client for getting congress info
    """

    _memberRepo: ICongressMemberRepository

    def __init__(self, memberRepo: ICongressMemberRepository) -> None:
        self._memberRepo = memberRepo

    def getSenators(self) -> pd.DataFrame:
        return self._memberRepo.getSenators().copy(deep=True)

    def getRepresentatives(self) -> pd.DataFrame:
        return self._memberRepo.getRepresentatives().copy(deep=True)

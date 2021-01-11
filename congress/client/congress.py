import pandas as pd
from congress.members.interface import ICongressMemberRepository


class Congress:
    _memberRepo: ICongressMemberRepository

    def __init__(self, memberRepo: ICongressMemberRepository) -> None:
        self._memberRepo = memberRepo

    def getSenators(self) -> pd.DataFrame:
        return self._memberRepo.getSenators()

    def getRepresentatives(self) -> pd.DataFrame:
        return self._memberRepo.getRepresentatives()
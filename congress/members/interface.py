from abc import ABC, abstractmethod

import pandas as pd


class ICongressMemberRepository(ABC):
    @abstractmethod
    def getRepresentatives(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def getSenators(self) -> pd.DataFrame:
        pass
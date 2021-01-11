from abc import ABC, abstractmethod
from congress.api.models import Congressman
from typing import List
import pandas as pd


class ICongressTransformationService(ABC):
    """
    translates API results into DataFrames
    """

    @abstractmethod
    def congressmembers(self, members: List[Congressman]) -> pd.DataFrame:
        pass
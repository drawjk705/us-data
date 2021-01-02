from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar


T = TypeVar("T")


class ICache(ABC, Generic[T]):
    @abstractmethod
    def put(self, resource: str, data: T):
        pass

    @abstractmethod
    def get(self, resource: str) -> Optional[T]:
        pass
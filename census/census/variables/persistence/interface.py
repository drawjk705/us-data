from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar


T = TypeVar("T")


class ICache(ABC, Generic[T]):
    @abstractmethod
    def put(self, resource: str, data: T) -> bool:
        """
        Adds `data` to the cache

        Args:
            resource (str): string path to identify the resource
            data (T): the data that's being cached

        Returns:
            bool: `True` if the data was persisted, `False` if not (e.g., the data already existed
                    in the cache).
        """
        pass

    @abstractmethod
    def get(self, resource: str) -> Optional[T]:
        pass
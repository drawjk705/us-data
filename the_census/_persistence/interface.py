from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class ICache(ABC, Generic[T]):
    """
    Cache for persisting query data,
    so we don't need to make repeat API calls.
    """

    _cache_path: Path

    @abstractmethod
    def put(self, resource: str, data: T) -> bool:
        """
        Adds `data` to the cache

        Args:
            resource (str): string path to identify the resource
            data (T): the data that's being cached

        Returns:
            bool: `True` if the data did not exist in the cache, `False` if it did
        """
        ...

    @abstractmethod
    def get(self, resource: str) -> Optional[T]:
        """
        Gets `resource` from the cache, if it exists, else `None`.

        Args:
            resource (str)

        Returns:
            Optional[T]
        """
        ...

    @property
    def cache_path(self) -> Path:
        return self._cache_path

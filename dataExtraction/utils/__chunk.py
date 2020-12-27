from typing import Generator, List,  TypeVar

T = TypeVar('T')


def chunk(_list: List[T], chunkSize: int) -> Generator[List[T], None, None]:
    for i in range(0, len(_list), chunkSize):
        yield _list[i:i+chunkSize]

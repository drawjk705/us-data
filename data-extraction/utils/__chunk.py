from typing import Generator, List,  TypeVar

T = TypeVar('T')


def chunk(_list: List[T], chunkSize: int) -> Generator[List[T], None, None]:
    """
    Splits a list into `chunkSize`-sized chunks

    Args:
        _list (List[T]): the list to chunk
        chunkSize (int): how many elements in each chunk

    Yields:
        Generator[List[T], None, None]
    """
    for i in range(0, len(_list), chunkSize):
        yield _list[i:i+chunkSize]

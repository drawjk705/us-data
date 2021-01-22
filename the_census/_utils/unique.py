from typing import Collection, List, Set, TypeVar

T = TypeVar("T")


def get_unique(items: Collection[T]) -> List[T]:
    """
    Get all unique elements in a list

    Args:
        items (List[T])

    Returns:
        List[T]: list with distinct items
    """

    unique_list: List[T] = []
    seen_items: Set[T] = set()

    for item in items:
        if item in seen_items:
            continue
        seen_items.add(item)
        unique_list.append(item)

    return unique_list

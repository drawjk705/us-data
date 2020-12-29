from typing import Dict


class Group:
    name: str
    description: str
    variables: str

    def __init__(self, jsonRes: Dict[str, str]) -> None:
        self.__dict__ = jsonRes

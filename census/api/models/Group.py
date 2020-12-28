class Group:
    name: str
    description: str
    variables: str

    def __init__(self, jsonRes: dict) -> None:
        self.__dict__ = jsonRes

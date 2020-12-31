from typing import Mapping


class VariableCode:
    code: str
    meaning: str

    def __init__(self, code: str, meaning: str) -> None:
        self.code = code
        self.meaning = meaning

    def __repr__(self) -> str:
        return self.__dict__.__repr__()


class VariableCodes:
    def __init__(self, **kwargs: dict) -> None:  # type: ignore
        for k, v in kwargs.items():
            self.__setattr__(k, v)  # type: ignore

    # type: ignore
    def addCodes(self, **codes: Mapping[str, VariableCode]) -> None:
        for k, v in codes.items():
            self.__setattr__(k, v)  # type: ignore

    def __repr__(self) -> str:
        return self.__dict__.__repr__()

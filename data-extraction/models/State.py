from typing import List


class State:
    def __init__(self, name: str) -> None:
        self.name = name
        self.districts: List[str] = []

    def addDistrict(self, district: str) -> None:
        self.districts.append(district)

    def __repr__(self) -> str:
        return f'name: {self.name}\n districts: {self.districts}'

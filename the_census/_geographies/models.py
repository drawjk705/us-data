from dataclasses import dataclass, field

from the_census._utils.clean_variable_name import clean_variable_name


@dataclass(frozen=True)
class GeoDomain:
    name: str
    code_or_wildcard: str = field(default="*")

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.name}:{self.code_or_wildcard}"


class SupportedGeoSet:
    def __init__(self) -> None:
        super().__init__()

    def add(self, *geoName: str):
        mapping = {clean_variable_name(name): name for name in geoName}
        self.__dict__.update(mapping)

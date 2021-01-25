from dataclasses import dataclass, field
from typing import Tuple, Union

from the_census._utils.clean_variable_name import clean_variable_name

GeoDomainTypes = Union["GeoDomain", Tuple[str, str], Tuple[str]]


@dataclass(frozen=True)
class GeoDomain:
    name: str
    code_or_wildcard: str = field(default="*")

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.name}:{self.code_or_wildcard}"

    @classmethod
    def _from(
        cls,
        geo_domain: Union[
            "GeoDomain",
            Tuple[
                str,
                str,
            ],
            Tuple[str],
        ],
    ) -> "GeoDomain":
        if isinstance(geo_domain, GeoDomain):
            return cls(geo_domain.name, geo_domain.code_or_wildcard)
        else:
            return cls(*geo_domain)


class SupportedGeoSet:
    def __init__(self) -> None:
        super().__init__()

    def add(self, *geo_name: str):
        mapping = {clean_variable_name(name): name for name in geo_name}
        self.__dict__.update(mapping)

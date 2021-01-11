from dataclasses import dataclass


@dataclass(frozen=True)
class CongressConfig:
    congress: int
    apiKey: str
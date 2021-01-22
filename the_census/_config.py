from dataclasses import dataclass

CACHE_DIR = "cache"


@dataclass(frozen=True)
class Config:
    """
    Stores basic information so that we don't need to
    pass the same variables around all of the time
    """

    year: int = 2020
    dataset: str = "acs"
    survey: str = "acs1"
    cache_dir: str = CACHE_DIR
    should_load_from_existing_cache: bool = False
    should_cache_on_disk: bool = False
    replace_column_headers: bool = False
    api_key: str = ""

# documentation:
# https://www.census.gov/data/developers/data-sets/acs-1year.html
from constants import API_BASE_URL

KEY = 'f4d37ba3bfe3d457cfcf10e2ae3e66bab7a2af16'


def buildUrl(get: str, _for: str = 'congressional district', _in: str = 'state:*') -> str:
    """
    Builds a URL to pull data from the census API

    Args:
        get (str): the `get` query param
        _for (str, optional): the `for` query param. Defaults to 'congressional district'.
        _in (str, optional): the `in` query param. Defaults to 'state:*'.

    Returns:
        str: the full URL
    """
    return f'{API_BASE_URL}?get={get}&for={_for}&in={_in}'

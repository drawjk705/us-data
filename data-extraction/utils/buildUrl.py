# documentation:
# https://www.census.gov/data/developers/data-sets/acs-5year.html
baseUrl = 'https://api.census.gov/data/2019/acs/acs5'
KEY = 'f4d37ba3bfe3d457cfcf10e2ae3e66bab7a2af16'


def buildUrl(get: str, _for: str = 'congressional district', _in: str = 'state:*') -> str:
    return f'{baseUrl}?get={get}&for={_for}&in={_in}'

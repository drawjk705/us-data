# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from census.getCensus import getCensus


c = getCensus(2019, shouldCacheOnDisk=True, shouldLoadFromExistingCache=True)


c.getGroups()


groups = c.getGroups()


internetSlashEducSearch = c.searchGroups(regex="(internet|education)")


c.searchGroups("^employment")

educAttainment = c.getVariablesByGroup(["C15003"])
compAccessByEduc = c.getVariablesByGroup(["B28006"])
educAndEmployment = c.getVariablesByGroup(["B16010"])
employment = c.getVariablesByGroup(["B23025"])

grouped = c.getVariablesByGroup(["C15003", "B28006", "B16010", "B23025"])

grouped = grouped[grouped["name"].str.contains("^Estimate!!")]


grouped.head()

from census.models import GeoDomain

variables = grouped["code"].tolist()
# %%

c.getStats(
    variables,
    GeoDomain("congressional district"),
    [GeoDomain("state")],
    replaceColumnHeaders=True,
)


# %%

# %%

# %%

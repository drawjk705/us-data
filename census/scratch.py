# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from census.getCensus import getCensus


# %%
c = getCensus(2019, shouldCacheOnDisk=True, shouldLoadFromExistingCache=True)


# %%
groups = c.getGroups()


# %%
educGroups = c.searchGroups("education")


# %%
c.searchGroups("computer").head()


# %%
# B16010    EDUCATIONAL ATTAINMENT AND EMPLOYMENT STATUS BY LANGUAGE SPOKEN AT HOME FOR THE POPULATION 25 YEARS AND OVER
# C15003	EDUCATIONAL ATTAINMENT FOR THE POPULATION 25 YEARS AND OVER
# B28010	COMPUTERS IN HOUSEHOLD
# B28003	PRESENCE OF A COMPUTER AND TYPE OF INTERNET SUBSCRIPTION IN
# B28006	EDUCATIONAL ATTAINMENT BY PRESENCE OF A COMPUTER AND TYPES OF INTERNET SUBSCRIPTION IN HOUSEHOLD
# B23025	EMPLOYMENT STATUS FOR THE POPULATION 16 YEARS AND OVER
# B27011	HEALTH INSURANCE COVERAGE STATUS AND TYPE BY EMPLOYMENT STATUS
# C16010	EDUCATIONAL ATTAINMENT AND EMPLOYMENT STATUS BY LANGUAGE SPOKEN AT HOME FOR THE POPULATION 25 YEARS AND OVER


# %%
from census.variables.models import GroupCode


# %%
variables = c.getVariablesByGroup(
    [
        "B16010",
        "C15003",
        "B28010",
        "B28003",
        "B28006",
        "B23025",
        "B27011",
        "C16010",
    ]
)


# %%
filteredVars = variables[variables["name"].str.contains("^estimate!!", case=False)]
# %%

filteredVars[["name", "code"]]
# %%

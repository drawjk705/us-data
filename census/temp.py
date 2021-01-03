# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from getCensus import getCensus
from census.models import GeoDomain


# %%
c = getCensus(2019, shouldLoadFromExistingCache=True)


# %%
c.getSupportedGeographies().head(n=20)


# %%
c.getGroups().head()


# %%
c.getVariablesByGroup(groups=["B17015"]).head()


# %%
c.getGeographyCodes(forDomain=GeoDomain("state")).head()


# %%
c.getGeographyCodes(
    forDomain=GeoDomain("county"), inDomains=[GeoDomain("state", "28")]
).head()


# %%
c.getStats(
    variablesToQuery=["B17015_001E", "B17015_002E", "B17015_003E"],
    forDomain=GeoDomain("county"),
    inDomains=[GeoDomain("state", "28")],
)


# %%

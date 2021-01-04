# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from getCensus import getCensus
from census.models import GeoDomain


# %%
c = getCensus(2020, shouldLoadFromExistingCache=True)

# %%

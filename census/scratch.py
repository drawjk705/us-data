# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

# %%
get_ipython().run_line_magic("config", "Completer.use_jedi = False")


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


# %%
from census.variables.models import GroupCode


# %%
variables = c.getVariablesByGroup(
    [
        "C15003",
        "B28010",
        "B28003",
        "B28006",
        "B23025",
        "B27011",
    ]
)


# %%
filteredVars = variables[variables["name"].str.contains("^estimate!!", case=False)]


# %%
varCodes = filteredVars["code"].tolist()


# %%
from census.models import GeoDomain


# %%
from census.utils.chunk import chunk
import pandas as pd


# %%
len(filteredVars)


# %%
df = filteredVars[filteredVars["groupCode"] == "C15003"]


# %%
df


# %%
educData = c.getStats(
    df["code"].tolist(),
    GeoDomain("congressional district"),
    [GeoDomain("state")],
    replaceColumnHeaders=True,
)


# %%
educData.head(n=2)


# %%
educData.columns


# %%
educData["pctNoHs"] = (
    educData.Estimate_Total_NoSchoolingCompleted
    + educData.Estimate_Total_NurseryTo4thGrade
    + educData.Estimate_Total_5thAnd6thGrade
    + educData.Estimate_Total_7thAnd8thGrade
    + educData.Estimate_Total_9thGrade
    + educData.Estimate_Total_10thGrade
    + educData.Estimate_Total_11thGrade
    + educData.Estimate_Total_12thGradeNoDiploma
) / educData.Estimate_Total


# %%

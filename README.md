# US-Stats

Want to work with US Census data? Look no further.

[TOC]

## Getting started

### Which dataset?

If you you're not sure what Census dataset you're interested in, the following code will take care of you:

```python3
from census import listAvailableDataSets()

listAvailableDataSets()
```

This will present you with a pandas DataFrame listing all available datasets from the US Census API. (This includes only aggregate datasets, as they other types [of which there are very few] don't play nice with the client).

### Querying a dataset

Say you're interested in the American Community Survey 1-year estimates for 2019. Look up the dataset and survey name in the table provided by `listAvailableDataSets`, and execute the following code:

```python3
from census import getCensus

dataset = getCensus(year=2019, datasetType="acs", surveyType="acs1")
```

The `acsData` object will now let you query any census data for the the ACS 1-year estimates of 2019. We'll now dive into how to query this dataset with the tool. However, if you aren't familiar with dataset "architecture", check out [this](#dataset-architecture) section.

#### Supported geographies

Getting the [supported geographies](#supported-geographies) for a dataset as as simple as this:

```python3
dataset.getSupportedGeographies()
```

This will output a DataFrame will all possible supported geographies (e.g., if I can query all school districts across all states).

#### Geography codes

If you decide you want to query a particular geography (e.g., a particular school district within a particular state), you'll need the [FIPS](https://en.wikipedia.org/wiki/Federal_Information_Processing_Standard_state_code#FIPS_state_codes) codes for that school district and state.

So, if you're interested in all school districts in Colorado, here's what you'd do:

1. Get FIPS codes for all states:

```python3
from census import GeoDomain

dataset.getGeographyCodes(GeoDomain("state", "*"))
```

2. Get FIPS codes for all school districts within Colorado (FIPS code `08`):

```python3
dataset.getGeographyCodes(GeoDomain("school district", "*"),
                          GeoDomain("state", "08"))
```

Note that geography code queries must follow supported geography guidelines

#### Groups

Want to figure out what groups are available for your dataset? No problem. This will do the trick for ya:

```python3
dataset.getGroups()
```

...and you'll get a DataFrame with all groups for your dataset.

##### Searching groups

`dataset.getGroups()` will return a lot of data that might be difficult to slog through. In that case, run this:

```python3
c.searchGroups(regex=r"my regex")
```

and you'll get a filtered DataFrame with matches to your regex.

##### Groups autocomplete

If you're working in a Jupyter notebook and have autocomplete enabled, you can

#### Variables

##### Searching variables

## Dataset "architecture"

US Census datasets have 3 primary components:

1.  [Groups](#groups)
2.  [Variables](#variables)
3.  [Supported Geographies](#supported-geographies)

### Groups

A group is a "category" of data gathered for a particular dataset. For example, the `SEX BY AGE` group would provide breakdowns of gender and age demographics in a given region in the United States.

Some of these groups' names, however, are a not as clear as `SEX BY AGE`. In that case, I recommend heading over to the survey in question's [technical documentation](https://www2.census.gov/programs-surveys/) which elaborates on what certain terms mean with respect to particular groups. Unfortunately, the above link might be complicated to navigate, but if you're looking for ACS group documentation, [here's](https://www2.census.gov/programs-surveys/acs/tech_docs/subject_definitions/2019_ACSSubjectDefinitions.pdf) a handy link.

### Variables

Variables measure a particular data-point. While they have their own codes, you might find variables which share the same name (e.g., `Estimate!!:Total:`). This is because each variable belongs to a [group](#group). So, the `Estimate!!:Total` variable for `SEX BY AGE` group is the total of all queried individuals in that group; but the `Estimate!!:Total` variable for `POVERTY STATUS IN THE PAST 12 MONTHS BY AGE` group is the total of queried individuals for _that_ group. (It's important when calculating percentages that you work within the same group. So if I want the percent of men in the US, whose total number I got from `SEX BY AGE` I should use the `Estimate!!:Total:` of that group as my denominator, and not the `Estimate!!:Total:` of the `POVERTY STATUS` group).

Variables on their own, however, do nothing. They mean something only when you query a particular [geography](#supported-geographies) for them.

### Supported Geographies

Supported geographies dictate the kinds of queries you can make for a given dataset. For example, in the ACS-1, I might be interested in looking at stats across all school districts. The survey's supported geographies will tell me if I can actually do that; or, if I need to refine my query to look at school districts in a given state or smaller region.

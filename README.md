# us-stats

This repository has code to generate SQL tables for a wide array of US Census data. This way, we can run SQL queries on this data, and not be tied to Excel for our data analysis.

## Pulling the data & setting up the Database

In order do that, we first must pull the data from the API, and get it into CSVs, which we can then import into a SQL database.

The code that controls this workstream can be found in `data-extraction`. Make sure that you run:

```bash
~ cd data-extraction
~ source ./bin/activate
~ pip3 install -r requirements.txt
```

Once that's done, you can run:

```bash
~ python3 main.py
```

and the rest will be done for you.

If you want the SQL database, schemas, and tables to be created, however, you must have [`sqlcmd`](https://docs.microsoft.com/en-us/sql/tools/sqlcmd-utility?view=sql-server-ver15) set up on your machine. This includes setting up a sysadmin password for `sqlcmd`, as you will be prompted for your password when the script tries to set up the SQL infrastructure from the CSV files.

If you do not complete this step, the script will likely error out on you; but your CSV files will still be intact, so you can work with those.

## Modifying or adding more to the Database

The census data we determine to pull is stored in the [`schemasToTables`](https://github.com/drawjk705/us-stats/blob/main/data-extraction/constants.py#L73) variable.

### Adding a schema

If you'd like to add another schema to the database, simply add another key to the outermost set of keys. For example:

```python
schemasToTables: Dict[str, Dict[str, str]] = {
    # other schemas up here
    'myNewSchema': {}
}
```

### Adding a table

To add more tables to any schema, simply do this:

```python
schemasToTables: Dict[str, Dict[str, str]] = {
    # other schemas up here
    'mySchema': {
        'myNewTable': 'concept'
    }
}
```

The `concept` must be string which can be found in the description column of the [groups information for the census data](https://api.census.gov/data/2019/acs/acs1/groups.html).

### Changing the census year or survey data

If you want census data from a particular year or survey, modify the `YEAR` and `SURVEY_TYPE` variables (here)[https://github.com/drawjk705/us-stats/blob/main/data-extraction/constants.py#L3-L4].

You must make sure that there existed such a survey for the given year, and that the `SURVEY_TYPE` is correct for the API route.

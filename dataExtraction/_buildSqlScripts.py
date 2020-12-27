from typing import List
from numpy.core.fromnumeric import shape
from constants import DATA_FILES_DIR, DB
from pathlib import Path

CREATE_DB_SQL = f"""
    use master

    print 'CREATING US_CENSUS DATABASE'

    if exists (
        select 1
    from master.sys.databases
    where name = '{DB}'
    )
    begin
        drop database {DB}
    end

    create database {DB}

    print 'US_CENSUS DATABASE CREATED'
    GO
"""


def __makeStateIdsSql() -> str:
    absPath = Path().absolute()

    SQL = f"""
    print 'CREATING TABLE stateIds'

    if exists (
        select 1
        from [{DB}].INFORMATION_SCHEMA.TABLES t
        where t.TABLE_NAME = 'stateIds'
    )
    begin
        drop table [{DB}].[dbo].[stateIds]
    end

    create table [{DB}].[dbo].[stateIds]
    (
        stateId varchar(32) primary key,
        [censusCode] varchar(32),
        [stateName] varchar(32),
        [stateAbbr] varchar(32),
        [district] varchar(32)
    )
    GO

    if OBJECT_ID('tempdb..#temp') is not null
    begin
        drop table #temp
    end

    create table #temp
    (
        [censusCode] varchar(32),
        [stateName] varchar(32),
        [stateAbbr] varchar(32),
        [district] varchar(32),
        stateId varchar(32)
    )
    GO

    bulk insert #temp
    from '{absPath}/{DATA_FILES_DIR}/dbo/stateIds.csv'
    with (
        fieldterminator = ',',
        firstrow = 2
    )
    GO

    insert into [{DB}].[dbo].[stateIds]
    select
        [stateId] as [stateId],
        [censusCode] as [censusCode],
        [stateName] as [stateName],
        [stateAbbr] as [stateAbbr],
        [district] as [district]
    from #temp
    GO

    print 'stateIds CREATED'

    GO
    """

    return SQL


def __writeTableColumnsSql(columnsStr: str, isTempTable: bool = False) -> str:
    columns = columnsStr.strip().split(',')
    columns = columns[:-1]

    columnType = 'varchar(32)' if isTempTable else 'bigint'

    stateIdColumnSql = '[stateId] varchar(32)' + \
        ('' if isTempTable else ' primary key')
    columnsSqlList = [f'[{col}] {columnType}' for col in columns]

    if isTempTable:
        columnsSqlList.append(stateIdColumnSql)
    else:
        columnsSqlList = [stateIdColumnSql] + columnsSqlList

    return ',\n'.join(columnsSqlList)


def __writeTransferFromTempToMainSql(columnsStr: str) -> str:
    columns = columnsStr.strip().split(',')
    stateIdColumn = columns[-1]
    otherColumns = columns[:-1]

    transferColumnsSqlList = [f'[{stateIdColumn}] as [{stateIdColumn}]'] + [
        f'cast([{col}] as bigint) as [{col}]' for col in otherColumns]

    return ',\n'.join(transferColumnsSqlList)


def __makeSqlForTable(tableFilePath: Path) -> str:
    schema = tableFilePath.parents[0].name
    tableName = Path(tableFilePath.name).with_suffix('').name

    topRow = ''
    with open(tableFilePath, 'r') as f:
        topRow = f.readline()

    mainTableColumnSql = __writeTableColumnsSql(topRow)
    tempTableColumnSql = __writeTableColumnsSql(topRow, isTempTable=True)
    transferFromTempToMainSql = __writeTransferFromTempToMainSql(topRow)

    SQL = f"""

    print 'CREATING TABLE {schema}.{tableName}'

    if exists (
        select 1
        from {DB}.INFORMATION_SCHEMA.tables
        where TABLE_NAME = '{tableName}'
    )
    begin
        drop table [{DB}].[{schema}].[{tableName}]
    end

    create table [{DB}].[{schema}].{tableName}
    (
        {mainTableColumnSql}

        constraint FK_{tableName}StateId_StateIdsStateId foreign key (stateId) references [{DB}].[dbo].StateIds(stateId)
    )
    GO

    if OBJECT_ID('tempdb..#temp') is not null
    begin
        drop table #temp
    end

    create table #temp
    (
        {tempTableColumnSql}
    )
    GO

    bulk insert #temp
    from '{tableFilePath.absolute()}'
    with (
        fieldterminator = ',',
        firstrow = 2
    )
    GO

    insert into [{DB}].[{schema}].[{tableName}]
    select
        {transferFromTempToMainSql}
    from #temp
    GO

    print 'CREATED {schema}.{tableName}'

    GO
    """

    return SQL


def __makeSchemaSql(schemaName: str) -> str:
    SQL = f"""
    if exists (
        select 1
        from sys.schemas
        where name = '{schemaName}'
    )
    begin
        exec('drop schema {schemaName}');
    end

    use {DB}

    print 'CREATING SCHEMA {schemaName}'

    exec('create schema {schemaName}');

    print 'CREATED SCHEMA {schemaName}'

    GO
    """

    return SQL


def buildSqlScripts():
    SQL = CREATE_DB_SQL + __makeStateIdsSql()

    for schema in Path(DATA_FILES_DIR).iterdir():
        if schema.name == 'dbo':
            continue

        SQL += __makeSchemaSql(schema.name)

        for table in schema.iterdir():
            SQL += __makeSqlForTable(table)

    with open('test.sql', 'w') as f:
        f.write(SQL)


buildSqlScripts()

import os
from pathlib import Path
from constants import DB, DATA_FILES_DIR


def __getColumnsSql(topRow: str, temp=False) -> str:
    columns = topRow.strip().split(',')
    columns = columns[:-1]
    columnType = 'varchar(32)' if temp else 'bigint'

    stateIdSql = '    stateId varchar(32)' + ('' if temp else ' primary key')

    columnSqlList = [f'    [{col}] {columnType}' for col in columns]
    if temp:
        columnSqlList.append(stateIdSql)
    else:
        columnSqlList.insert(0, stateIdSql)

    return ',\n'.join(columnSqlList)


def __getTransferColumnsSql(topRow: str) -> str:
    columns = topRow.strip().split(',')
    stateIdColumn = columns[-1]
    columns = columns[:-1]

    transferColumnsSqlList = [
        f'    cast([{col}] as bigint) as [{col}]' for col in columns]
    transferColumnsSqlList.insert(0,
                                  f'    [{stateIdColumn}] as [{stateIdColumn}]')

    return ',\n'.join(transferColumnsSqlList)


def __createSqlForCsv(filename: str) -> str:
    tableName = Path(filename).with_suffix('')
    topRow = ''
    with open(f'{DATA_FILES_DIR}/{filename}', 'r') as f:
        topRow = f.readline()

    columnsSql = __getColumnsSql(topRow)
    tempColumnsSql = __getColumnsSql(topRow, temp=True)
    transferColumnsSql = __getTransferColumnsSql(topRow)

    absPath = os.getcwd()

    return f"""use {DB}

print 'CREATING TABLE {tableName}'

if exists (
    select 1
from {DB}.INFORMATION_SCHEMA.TABLES t
where t.TABLE_NAME = '{tableName}'
)
begin
    drop table {tableName}
end

create table {tableName}
(
{columnsSql},
    constraint FK_{tableName}StateId_StateIdsStateId foreign key (stateId) references stateIds(stateId)
)

if OBJECT_ID('tempdb..#temp') is not null
begin
    drop table #temp
end

create table #temp
(
{tempColumnsSql}
)

bulk insert #temp
from '{absPath}/{DATA_FILES_DIR}/{filename}'
with (
    fieldterminator = ',',
    firstrow = 2
)

insert into {tableName}
select
{transferColumnsSql}
from #temp

print '{tableName} CREATED'
"""


def generateSqlScripts():
    csvFiles = os.listdir('./dataFiles')

    for file in csvFiles:
        sql = __createSqlForCsv(file)
        yield sql

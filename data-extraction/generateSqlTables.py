import os
from pathlib import Path

DIR = 'dataFiles'


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


def generateSql(filename: str) -> str:
    tableName = Path(filename).with_suffix('')
    topRow = ''
    with open(f'{DIR}/{filename}', 'r') as f:
        topRow = f.readline()

    columnsSql = __getColumnsSql(topRow)
    tempColumnsSql = __getColumnsSql(topRow, temp=True)
    transferColumnsSql = __getTransferColumnsSql(topRow)

    absPath = os.getcwd()

    return f"""use states
    
if not exists (
    select 1
from states.INFORMATION_SCHEMA.TABLES t
where t.TABLE_NAME = '{tableName}'
)
begin
    create table {tableName}
    (
{columnsSql},
        constraint FK_{tableName}StateId_StateIdsStateId foreign key (stateId) references stateIds(stateId)
    )
end

exec master.dbo.maybeDropTemp

create table #temp
(
{tempColumnsSql}
)

bulk insert #temp
from '{absPath}/{DIR}/{filename}'
with (
    fieldterminator = ',',
    firstrow = 2
)

insert into {tableName}
select
{transferColumnsSql}
from #temp

select *
from {tableName}
"""


csvFiles = os.listdir('./dataFiles')

for file in csvFiles:
    sql = generateSql(file)
    name = Path(file).with_suffix('.sql')
    with open(f'../db-scripts/setup/{name}', 'w') as f:
        f.write(sql)

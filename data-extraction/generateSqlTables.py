import os
from typing import List

DIR = 'dataFiles'


def getColumns(topRow: str) -> List[str]:


def generateSql(filename: str) -> str:
    topRow = ''
    with open(f'{DIR}/{filename}', 'r') as f:
        topRow = f.readline()

    return f"""use states
if not exists (
    select 1
from states.INFORMATION_SCHEMA.TABLES t
where t.TABLE_NAME = '{0}'
)
begin
    create table {0}
    (
        stateId varchar(32) primary key,
        {1},

        constraint FK_{0}StateId_StateIdsStateId foreign key (stateId) references stateIds(stateId)
    )
end

exec master.dbo.maybeDropTemp

bulk insert #temp
from '{2}{0}'

create table #temp
(
    stateId varchar(32) primary key,
    total varchar(32),
    noIncome varchar(32),
    [$1-9k] varchar(32),
    [$10-15k] varchar(32),
    [$15-25k] varchar(32),
    [$25-35k] varchar(32),
    [$35-50k] varchar(32),
    [$50-65k] varchar(32),
    [$65-75k] varchar(32),
    [$75k-more] varchar(32),
)

insert into income
select
    stateId as stateId,
    cast(total as bigint) as total,
    cast(noIncome as bigint) as noIncome,
    cast([$1-9k] as bigint) as [$1-9k],
    cast([$10-15k] as bigint) as [$10-15k],
    cast([$15-25k] as bigint) as [$15-25k],
    cast([$25-35k] as bigint) as [$25-35k],
    cast([$35-50k] as bigint) as [$35-50k],
    cast([$50-65k] as bigint) as [$50-65k],
    cast([$65-75k] as bigint) as [$65-75k],
    cast([$75k-more] as bigint) as [$75k-more]
from #temp

select *
from income
"""


csvFiles = os.listdir('./dataFiles'):

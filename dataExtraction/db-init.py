from constants import DB


CREATE_DB_SQL = f"""use master

print 'CREATING {DB} DATABASE'

if exists (
    select 1
from master.sys.databases
where name = '{DB}'
)
begin
    drop database {DB}
end

create database {DB}

print '{DB} DATABASE CREATED'
GO
"""

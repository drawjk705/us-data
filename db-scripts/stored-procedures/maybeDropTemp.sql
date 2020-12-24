create proc maybeDropTemp
as
if OBJECT_ID('tempdb..#temp') is not null
begin
    drop table #temp
end


option Explicit
Const Backup_Server = "localhost"		' name of SQL server
Dim Connection
Dim Recordset
Dim SQL

SQL = "SELECT * FROM (SELECT DISTINCT [rhostid], [fqdnNames], [nodeDescription], [lastBackupStartTime], [lastBackupJobStatus], [RecPointStatus], [recPointCount], ROW_NUMBER() OVER(PARTITION BY rhostid ORDER BY lastBackupStartTime DESC) AS row_number FROM dbo.as_edge_host EH LEFT JOIN dbo.as_edge_host_d2dStatusInfo D2D ON EH.rhostid = D2D.hostId) a WHERE row_number = 1;"

Set Connection = CreateObject("ADODB.Connection")
Set Recordset = CreateObject("ADODB.Recordset")

Connection.Open "Provider=SQLOLEDB;Data Source=" & Backup_Server & "\ARCSERVE_APP;" & _ 
        "Trusted_Connection=Yes;Initial Catalog=arcserveUDP;"

Recordset.Open SQL,Connection
wscript.echo "<<<udp_backup:sep(124)>>>"

If Recordset.EOF Then 
  WScript.echo "There are no backup records to retrieve."
  Wscript.Quit(0)
Else 
  Do While NOT Recordset.EOF
    If Not (Len("" & Recordset("fqdnNames")) <= 2) then
      WScript.echo Recordset("rhostid") & "|" & replace(Recordset("fqdnNames"),",","") & "|" & Recordset("lastBackupStartTime") & "|" & Recordset("recPointCount") & "|" & Recordset("RecPointStatus") & "|" & Recordset("lastBackupJobStatus")
    End If
    Recordset.MoveNext     
  Loop
End If

Recordset.Close

SQL = "SELECT * FROM (SELECT DISTINCT [rhostid], [fqdnNames], [jobUTCStartTime], [jobStatus], [protectedDataSize], [jobMethod], ROW_NUMBER() OVER(PARTITION BY rhostid ORDER BY jobUTCStartTime DESC) AS row_number FROM dbo.as_edge_host EH LEFT JOIN dbo.as_edge_dashboard_d2d_jobhistory_details_view D2D ON EH.rhostid = D2D.agentId) a WHERE row_number = 1;"

Recordset.Open SQL,Connection
wscript.echo "<<<udp_jobs:sep(124)>>>"

If Recordset.EOF Then 
  WScript.echo "There are no backup records to retrieve."
  Wscript.Quit(0)
Else 
  Do While NOT Recordset.EOF
    If Not (Len("" & Recordset("fqdnNames")) <= 2) then
      WScript.echo Recordset("rhostid") & "|" & replace(Recordset("fqdnNames"),",","") & "|" & Recordset("jobUTCStartTime") & "|" & Recordset("jobStatus") & "|" & Recordset("protectedDataSize") & "|" & Recordset("jobMethod")
    End If
    Recordset.MoveNext     
  Loop
End If

Recordset.Close
Set Recordset=nothing
Connection.Close
Set Connection=Nothing
Wscript.Quit(0)

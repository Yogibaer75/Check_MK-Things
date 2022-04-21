###

$pswindow = $host.ui.rawui
$newsize = $pswindow.buffersize
$newsize.height = 300
$newsize.width = 200
$pswindow.Set_BufferSize($newsize)

###
write-host("<<<>>>")

function GetSQLData($sqlCmd) {
   # Create an adapter to put the data we get from SQL and get the data
   $sqlAdapter = New-Object System.Data.SqlClient.SqlDataAdapter
   $sqlAdapter.SelectCommand = $sqlCmd
   $dataSet = New-Object System.Data.DataSet
   $sqlAdapter.Fill($dataSet, "Result")
   return $dataSet
}

$hostname = $env:computername
$sqlConnection = New-Object System.Data.SqlClient.SqlConnection
$sqlConnection.ConnectionString = "Server=$hostname\ARCSERVE_APP;Integrated Security=True;Database=arcserveUDP"
$sqlConnection.Open()

# Create a command object
$sqlCmd = New-Object System.Data.SqlClient.SqlCommand
$sqlCmd.Connection = $sqlConnection

$sqlCmd.CommandText = "SELECT * FROM (SELECT DISTINCT [rhostid], [fqdnNames], [Rhostname], [lastBackupStartTime], [lastBackupJobStatus], [RecPointStatus], [recPointCount], ROW_NUMBER() OVER(PARTITION BY rhostid ORDER BY lastBackupStartTime DESC) AS row_number FROM dbo.as_edge_host EH LEFT JOIN dbo.as_edge_host_d2dStatusInfo D2D ON EH.rhostid = D2D.hostId) a WHERE row_number = 1;"
$result1 = GetSQLData($sqlCmd)

Write-Host("<<<udp_backup:sep(124)>>>")
foreach ($Row in $result1.Tables[0].Rows)
{
   if (-not [string]::IsNullOrEmpty($Row.Item(1)))
   {
      '{0}|{1}|{2}|{3}|{4}|{5}' -f $Row.rhostid, $Row.Rhostname, $Row.lastBackupStartTime, $Row.lastBackupJobStatus, $Row.RecPointStatus, $Row.recPointCount 
   }
}

$sqlCmd.CommandText = "SELECT * FROM (SELECT DISTINCT [rhostid], [fqdnNames], [Rhostname], [jobUTCStartTime], [jobStatus], [protectedDataSize], [jobMethod], ROW_NUMBER() OVER(PARTITION BY rhostid ORDER BY jobUTCStartTime DESC) AS row_number FROM dbo.as_edge_host EH LEFT JOIN dbo.as_edge_dashboard_d2d_jobhistory_details_view D2D ON EH.rhostid = D2D.agentId) a WHERE row_number = 1;"
$result2 = GetSQLData($sqlCmd)

Write-Host("<<<udp_jobs:sep(124)")
foreach ($Row in $result2.Tables[0].Rows)
{
   if (-not [string]::IsNullOrEmpty($Row.Item(1)))
   {
      '{0}|{1}|{2}|{3}|{4}|{5}' -f $Row.rhostid, $Row.Rhostname, $Row.jobUTCStartTime, $Row.jobStatus, $Row.protectedDataSize, $Row.jobMethod 
   }
}

$sqlConnection.Close()

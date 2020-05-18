$sqlserver = "localhost"
function GetUDPStatus($sqlCmd) {
   # Create an adapter to put the data we get from SQL and get the data
   $sqlAdapter = New-Object System.Data.SqlClient.SqlDataAdapter
   $sqlAdapter.SelectCommand = $sqlCmd
   $dataSet = New-Object System.Data.DataSet
   $sqlAdapter.Fill($dataSet)

   return $dataSet.Tables[0]
}

$sqlConnection = New-Object System.Data.SqlClient.SqlConnection
$sqlConnection.ConnectionString = "Server=$sqlServer;Integrated Security=True;Database=ARCSERVE_APP"
$sqlConnection.Open()

# Create a command object
$sqlCmd = New-Object System.Data.SqlClient.SqlCommand
$sqlCmd.Connection = $sqlConnection

$sqlCmd.CommandText = "SELECT * FROM (SELECT DISTINCT [rhostid], [fqdnNames], [nodeDescription], [lastBackupStartTime], [lastBackupJobStatus], [RecPointStatus], [recPointCount], ROW_NUMBER() OVER(PARTITION BY rhostid ORDER BY lastBackupStartTime DESC) AS row_number FROM dbo.as_edge_host EH LEFT JOIN dbo.as_edge_host_d2dStatusInfo D2D ON EH.rhostid = D2D.hostId) a WHERE row_number = 1;"
$recpointresult = GetUDPStatus($sqlCmd)

Write-Host("<<<udp_recpoints:sep(124)>>>")
Write-Host($recpointresult)

$sqlCmd.CommandText = "SELECT * FROM (SELECT DISTINCT [rhostid], [fqdnNames], [jobUTCStartTime], [jobStatus], [protectedDataSize], [jobMethod], ROW_NUMBER() OVER(PARTITION BY rhostid ORDER BY jobUTCStartTime DESC) AS row_number FROM dbo.as_edge_host EH LEFT JOIN dbo.as_edge_dashboard_d2d_jobhistory_details_view D2D ON EH.rhostid = D2D.agentId) a WHERE row_number = 1;"
$backupresult = GetUDPStatus($sqlCmd)

Write-Host("<<<udp_jobs:sep(124)")
Write-Host($backupresult)

$sqlConnection.Close()

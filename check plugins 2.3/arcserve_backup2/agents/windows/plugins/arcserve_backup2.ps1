###

$pshost = Get-Host              # Get the PowerShell Host.
$pswindow = $pshost.UI.RawUI    # Get the PowerShell Host's UI.

$newsize = $pswindow.BufferSize # Get the UI's current Buffer Size.
$newsize.height = 300          # Set the new buffer's heigt to 300 lines.
$newsize.width = 200            # Set the new buffer's width to 200 columns.
$pswindow.buffersize = $newsize # Set the new Buffer Size as active.

$newsize = $pswindow.windowsize # Get the UI's current Window Size.
$newsize.width = 200            # Set the new Window Width to 200 columns.
$pswindow.windowsize = $newsize # Set the new Window Size as active.

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($true)

###

function Backup($sqlCmd) {
    # 4319 - Menge Daten, 4400 - Zeit der Subjobs, 4310 - Anzahl Files, 4354 - Status des Jobs, 7936 - Name of Job, 4498 - Beschreibung
    $sqlCmd.CommandText = "SELECT top 100 jobid,logtime,serverhost,agenthost,msgtextid,msgtext FROM dbo.aslogw WHERE msgtextid IN ('4319','4310','4354','4373','4498','7936') ORDER BY jobid DESC, logtime DESC, msgtextid DESC;"
    # Testcommand output all
    #$sqlCmd.CommandText = "SELECT top 500 * FROM dbo.aslogw ORDER BY logtime DESC;"
    # Create an adapter to put the data we get from SQL and get the data
    $sqlAdapter = New-Object System.Data.SqlClient.SqlDataAdapter
    $sqlAdapter.SelectCommand = $sqlCmd
    $dataSet = New-Object System.Data.DataSet
    $sqlAdapter.Fill($dataSet)

    return $dataSet
}
$sqlConnection = New-Object System.Data.SqlClient.SqlConnection
$sqlConnection.ConnectionString = 'Server=back02\ARCSERVE_DB;Integrated Security=True;Database=aslog'
$sqlConnection.Open()

# Create a command object
$sqlCmd = New-Object System.Data.SqlClient.SqlCommand
$sqlCmd.Connection = $sqlConnection

$result1 = Backup($sqlCmd)
write-host("<<<arcserver_backup2:sep(124)>>>")
($result1.Tables[0].Columns | Select-Object -ExpandProperty ColumnName) -join '|'
foreach ($Row in $result1.Tables[0].Rows) {
    if (-not [string]::IsNullOrEmpty($Row)) {
        write-host(($Row.ItemArray) -join '|')
    }
}


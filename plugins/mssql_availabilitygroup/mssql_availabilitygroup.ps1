if (-not(Get-Module -Name SQLPS)) {
    if (Get-Module -ListAvailable -Name SQLPS) {
        Push-Location
        Import-Module -Name SQLPS -DisableNameChecking
        Pop-Location
    }
}

# Set debug to 1 to turn it on, set to zero to turn it off
# if debug is on, debug messages are shown on the screen
$DEBUG=0

Function debug_echo {
Param(
 [Parameter(Mandatory=$True,Position=1)]
   [string]$error_message
)
     # if debug=1 then output
     if ($DEBUG -gt 0) {
          echo "DEBUG:${error_message}"
     }
}

# Fallback if the (old) agent does not provide the MK_CONFDIR
if (!$MK_CONFDIR) {
    $MK_CONFDIR= "c:\Program Files\check_mk\config"
}

# Source the needed configuration file for this agent plugin
$CONFIG_FILE="${MK_CONFDIR}\mssql_availability_status_cfg.ps1"
if (test-path -path "${CONFIG_FILE}" ) {
     debug_echo "${CONFIG_FILE} found, reading"
     . "${CONFIG_FILE}"
} else {
    debug_echo "${CONFIG_FILE} not found"
}

if ($SQLAVAIL) {
     $ServerName=""
     $GroupName=""
     foreach ($entry in $SQLAVAIL) {
          $counter=$counter + 1
          switch ($counter) {
                  1 {$ServerName=$entry}
                  2 {$GroupName=$entry}
                  default {"Error handling MSSQL database connection with config for Server and Group name."}
          }
     }
     debug_echo "value of server is $ServerName and the group is $GroupName"
} else {
     debug_echo "no server and group defined"
}

# Connect to the server instance and set default init fields for 
# efficient loading of collections. We use windows authentication here,
# but this can be changed to use SQL Authentication if required.
$serverObject = New-Object Microsoft.SqlServer.Management.SMO.Server($ServerName)
$serverObject.SetDefaultInitFields([Microsoft.SqlServer.Management.Smo.AvailabilityGroup], $true)
$serverObject.SetDefaultInitFields([Microsoft.SqlServer.Management.Smo.AvailabilityReplica], $true)
$serverObject.SetDefaultInitFields([Microsoft.SqlServer.Management.Smo.DatabaseReplicaState], $true)

# Attempt to access the availability group object on the server
$groupObject = $serverObject.AvailabilityGroups[$GroupName]

if($groupObject -eq $null)
{
    # Can't find the availability group on the server.
    Write-Host "<<<sql_availabilitygroup>>>"
    Write-Host "The availability group '$GroupName' does not exist on server '$ServerName'."
}
elseif($groupObject.PrimaryReplicaServerName -eq $null)
{
    # Can't determine the primary server instance. This can be serious (may mean the AG is offline), so throw an error.
    Write-Host "<<<sql_availabilitygroup>>>"
    Write-Host "Cannot determine the primary replica of availability group '$GroupName' from server instance '$ServerName'. Please investigate!" 
}
elseif($groupObject.PrimaryReplicaServerName -ne $ServerName)
{
    # We're trying to run the script on a secondary replica, which we shouldn't do.
    # We'll just throw a warning in this case, however, and skip health evaluation.
    Write-Host "<<<sql_availabilitygroup>>>"
    Write-Host "<<<sql_availabilityreplicas>>>"
    Write-Host "<<<sql_databasereplicastate>>>"
}
else 
{
    $groupResult = Test-SqlAvailabilityGroup $groupObject -NoRefresh
    $replicaResults = @($groupObject.AvailabilityReplicas | Test-SqlAvailabilityReplica -NoRefresh)
    $databaseResults = @($groupObject.DatabaseReplicaStates | Test-SqlDatabaseReplicaState -NoRefresh)
    Write-Host "<<<sql_availabilitygroup>>>"
    $groupResult | ft HealthState,Name -AutoSize -HideTableHeader
    Write-Host "<<<sql_availabilityreplicas>>>"
    $replicaResults | ft HealthState,AvailabilityGroup,Name -AutoSize -HideTableHeader
    Write-Host "<<<sql_databasereplicastate>>>"
    $databaseResults | ft HealthState,AvailabilityGroup,AvailabilityReplica,Name -AutoSize -HideTableHeader
}


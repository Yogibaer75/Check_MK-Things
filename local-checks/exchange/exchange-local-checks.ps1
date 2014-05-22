#
# PSSnapin Load
if ( (Get-PSSnapin -Name Microsoft.Exchange.Management.PowerShell.E2010 -ErrorAction SilentlyContinue) -eq $null )
{
    Add-PsSnapin Microsoft.Exchange.Management.PowerShell.E2010
}

# Test Mailbox Database Health
# 
# This script will look at all mailbox databases
# and determine the status of each.

$NagiosStatus = "3"
$NagiosDescription = ""

ForEach ($DataBase in Get-MailboxDatabase) {
	ForEach ($Status in Get-MailboxDatabaseCopyStatus -Identity $DataBase.Name) {
		switch ($Status.Status) {
			"FailedandSuspended" { 
				$NagiosStatus = "2"
				if ($NagiosDescription -ne "") {
					$NagiosDescription = $NagiosDescription + ", "
				}
				$NagiosDescription = $NagiosDescription + $Status.Name + " is " + $Status.Status
			}
				
			"Failed" { 
				$NagiosStatus = "2"
				if ($NagiosDescription -ne "") {
					$NagiosDescription = $NagiosDescription + ", "
				}
				$NagiosDescription = $NagiosDescription + $Status.Name + " is " + $Status.Status
			}	

			"Seeding" { 
				$NagiosStatus = "2"
				if ($NagiosDescription -ne "") {
					$NagiosDescription = $NagiosDescription + ", "
				}
				$NagiosDescription = $NagiosDescription + $Status.Name + " is " + $Status.Status
			}	
	
			"Dismounted" {
				$NagiosStatus = "2"
				if ($NagiosDescription -ne "") {
					$NagiosDescription = $NagiosDescription + ", "
				}
				$NagiosDescription = $NagiosDescription + $Status.Name + " is " + $Status.Status
			}
				
			"Resynchronizing" {
				if ($NagiosStatus -ne "2") {
					$NagiosStatus = "1"
				}
				if ($NagiosDescription -ne "") {
					$NagiosDescription = $NagiosDescription + ", "
				}
				$NagiosDescription = $NagiosDescription + $Status.Name + " is " + $Status.Status
			}

			"Suspended" {
				if ($NagiosStatus -ne "2") {
					$NagiosStatus = "1"
				}
				if ($NagiosDescription -ne "") {
					$NagiosDescription = $NagiosDescription + ", "
				}
				$NagiosDescription = $NagiosDescription + $Status.Name + " is " + $Status.Status
			}

			"Mounting" {
				if ($NagiosStatus -ne "2") {
					$NagiosStatus = "1"
				}
				if ($NagiosDescription -ne "") {
					$NagiosDescription = $NagiosDescription + ", "
				}
				$NagiosDescription = $NagiosDescription + $Status.Name + " is " + $Status.Status
			}

			"Healthy" {
				if ($NagiosStatus -ne "2") {
					if ($NagiosStatus -ne "1") {
						$NagiosStatus = "0"
				}}
			}
			"Mounted" {
				if ($NagiosStatus -ne "2") {
					if ($NagiosStatus -ne "1") {
						$NagiosDescription = "All Mailbox Databases are mounted and healthy."
						$NagiosStatus = "0"
				}}
			}
		}
	}
}

Write-Host "$NagiosStatus Exchange-Mailbox-Health - $NagiosDescription"

#
# IMAP Check
#

$status = 2;
$desc = "";
$latency = 0;

test-imapconnectivity | ForEach-Object {
    if($_.Result -like "Erfolgreich") {
        $latency=$_.LatencyInMillisecondsString;
        $status=0;
	$desc="IMAP Check latency $latency ms"
    } elseif($_.Result -like "Fehler") {
        $desc="IMAP Failure"
        $status=2;
    } else {
        # Somethings up..
        $status=2;
        $desc="Unknown Failure"
    }
}

Write-Host "$status Exchange-IMAP latency=$latency $desc"

#
# MAPI Check
#

$status = 2;
$desc = "";

test-mapiconnectivity | ForEach-Object {
    if($_.Result -like "Erfolgreich") {
	$status = 0;
	$desc="MAPI OK"
    } elseif($_.Result -like "Fehler") {
        $desc="MAPI Failure " + $_.Database;
        $status=2;
    } else {
        # Somethings up..
        $status=2;
        $desc="Unknown Failure"
    }
}

Write-Host "$status Exchange-Mapi - $desc"

#
# Outlook TCP Connect Check
#

$status = 2;
$desc = "";

test-outlookconnectivity -protocol tcp | ForEach-Object {
    if($_.Result -like "Erfolgreich") {
	$status = 0;
	$desc="Outlook Connectivity OK"
    } elseif($_.Result -like "Fehler") {
        $status=2;
        $desc="Outlook Connectivity Failure " + $_.Scenario;
    } else {
        $status=2;
        $desc="Unknown Failure"
    }
}

Write-Host "$status Exchange-OutlookTCP - $desc"

#
# OWA
#


$status = 2;
$desc = "";
$latency = 0;
$url = "";

test-owaconnectivity | ForEach-Object {
    if($_.Result -like "Erfolgreich") {
        $latency=$_.LatencyInMillisecondsString;
	$status = 0;
        $desc="OWA OK"
    } elseif($_.Result -like "Fehler") {
        $desc="OWA Failure"
        $status=2;
    } else {
        $status=2;
        $desc="Unknown Failure"
    }
    $url = $_.URL;
}

Write-Host "$status Exchange-OWA latency=$latency $desc $url"

#
# POP3
#

$status = 2;
$desc = "";
$latency = 0;

test-popconnectivity | ForEach-Object {
    if($_.Result -like "Erfolgreich") {
        $latency=$_.LatencyInMillisecondsString;
        $status=0;
	$desc="POP3 OK check latency $latency ms"
    } elseif($_.Result -like "Fehler") {
        $desc="POP3 Failure"
        $status=2;
    } else {
        # Somethings up..
        $status=2;
        $desc="Unknown Failure"
    }
}

Write-Host "$status Exchange-POP3 latency=$latency $desc"

#
# Public Folders
#

try
	{
		try
			{
				$Result = Get-PublicFolder -Server $env:computername -ErrorAction Stop
				Write-Host "0 Exchange-Public-Folders - Public folders are mounted."
			}
		catch [System.Management.Automation.ActionPreferenceStopException]
			{
				Throw $_.exception
			}
		catch
			{
				Throw $_.exception
			}
	} 
catch
	{
		Write-Host "2 Exchange-Public-Folders - Public Folders Database is dismounted."
	}

#
# Replication Health
#

$NagiosStatus = "0"
$NagiosDescription = ""

ForEach ($Type in Test-ReplicationHealth -Identity $env:computername) {

 	# Look for failed replications
	if ($TypeResult -like "*FAILED*") {
		# Format the output for Nagios
		if ($NagiosDescription -ne "") {
			$NagiosDescription = $NagiosDescription + ", "
		}
		
		$NagiosDescription = $NagiosDescription + $Type.Check + $Type.Result
		
		# Set the status to failed.
		$NagiosStatus = "2"
		
	# Look for warnings in replication
	} elseif ($Type.Check -like "*Warn*") {
		# Format the output for Nagios
		if ($NagiosDescription -ne "") {
			$NagiosDescription = $NagiosDescription + ", "
		}
		
		$NagiosDescription = $NagiosDescription + $Type.Check + $Type.Result
		
		# Don't lower the status level if we already have
		# a failed attempt
		if ($NagiosStatus -ne "2") {
			$NagiosStatus = "1"
		}
	} 
}

# Output, what level should we tell our caller?
if (($NagiosStatus -eq "0") -and ($NagiosDescription -eq "")){
	$NagiosDescription = "All replication tests passed."
}

Write-Host "$NagiosStatus Exchange-Replication-Health - $NagiosDescription"

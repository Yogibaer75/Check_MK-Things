#
# Hyper-V VM state
#
# Script must executed with local administrator credentials!
#
# This script gathers a few information about VM integration services,
# checkpoints and replication. All other information about the system
# health are gathered by the operating system agents on both, host and
# guest servers
#
# Version: 1.0
#
# Date: 2015-08-01
#
# Author: A. Exner, ACP

# Get VM's from host and collect informations

$VMList = Get-VM
$now = Get-Date

Foreach ($VM in $VMList)
{
    $name = $VM.name
    $vmversion = $VM.IntegrationServicesVersion
    $vmupdate = $VM.IntegrationServicesState
    Write-Host "<<<<$name>>>>"
    Write-Host "<<<hyperv_vmstatus>>>"

    # Integration Services

    If ($VM.state -match "Running")
    {
    $VMI = Get-VMIntegrationService -VMName $VM.name
    $VMIStat = $VMI | Where-Object {$_.PrimaryStatusDescription -NotMatch "Ok"}

    If($VMIStat.Count -gt 0)
    {
        Write-Host "Integration_Services Protocol_Mismatch"
        $VMIProb = $VMIStat | ForEach-Object{ "{0,-20}" -f $_.Name -replace '\s+$','' -replace ' ','_'}
        Write-Host "Problems $VMIProb"
    }
    Else
    {
        Write-Host "Integration_Services Ok"
    }
    }
    Else
    {
        Write-Host "Integration_Services Stopped"
    }

    #Replica
    $status = Get-VMReplication $VM.Name -ErrorAction:SilentlyContinue | ForEach-Object{ "{0,-20}{1,-20}{2,-10}{3,-60}" -f $_.State,$_.Health,$_.Mode,$env:computername }
    Write-Host "Replica_Health " $status
    Write-Host "Host " $env:COMPUTERNAME
    
    #Checkpoints
    $VMCP = Get-VMSnapshot -VMName $VM.name
    Write-Host "<<<hyperv_checkpoints>>>"
    If ($VMCP)
    {
        Foreach($CP in $VMCP)
        {
            $OutputString = [string]$CP.Id + " " + [string][System.Math]::Round((($now - $CP.CreationTime).TotalSeconds), 0)
            Write-Host $OutputString
        }
    }
    Else
    {
        Write-Host "No_Checkpoints"
    }

    Write-Host "<<<hyperv_intgrversion>>>"
    write-Host $vmversion
    write-Host $vmupdate
}

Write-Host "<<<<>>>>"

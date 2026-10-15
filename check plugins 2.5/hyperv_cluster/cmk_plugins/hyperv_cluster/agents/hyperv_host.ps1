# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
# Optimized & Bugfixed Version

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($true)

function Get-VMGeneralInfo {
  param(
    [Object]$vm,
    [Object]$VMReplica = $null,
    [bool]$HasVMSecurity = $false
  )

  $guestData = [ordered]@{
    'guest.fqdn' = $null
    'guest.os' = $null
    'guest.IntegrationServicesVersion' = $null
  }

  try {
    $VMWMI = Get-CimInstance -Namespace root\virtualization\v2 -Class Msvm_ComputerSystem -Filter "ElementName='$($vm.Name)'" -ErrorAction SilentlyContinue
    if ($null -ne $VMWMI) {
      $kvpExchange = Get-CimAssociatedInstance -InputObject $VMWMI -ResultClass Msvm_KvpExchangeComponent -ErrorAction SilentlyContinue
      if ($null -ne $kvpExchange) {
        foreach ($exchangeItem in $kvpExchange.GuestIntrinsicExchangeItems) {
          $xml = [xml]$exchangeItem
          $propName = $xml.SelectSingleNode("/INSTANCE/PROPERTY[@NAME='Name']/VALUE")
          if ($null -ne $propName) {
            $propName = $propName.InnerText
            $dataValue = $xml.SelectSingleNode("/INSTANCE/PROPERTY[@NAME='Data']/VALUE")
            if ($null -ne $dataValue) {
              switch ($propName) {
                'FullyQualifiedDomainName' { $guestData.'guest.fqdn' = $dataValue.InnerText }
                'OSName' { $guestData.'guest.os' = $dataValue.InnerText }
                'IntegrationServicesVersion' { $guestData.'guest.IntegrationServicesVersion' = $dataValue.InnerText }
              }
            }
          }
        }
      }
    }
  } catch {
    Write-Verbose "Failed to retrieve KVP data for VM '$($vm.Name)': $_"
  }

  $VMSec = @{}
  if ($HasVMSecurity) {
    $SecData = Get-VMSecurity -VM $vm | Select-Object Shielded, TpmEnabled, KsdEnabled, EncryptStateAndVmMigrationTraffic
    $VMSec = [ordered]@{
      'security.shieldedVM' = $secData.Shielded
      'security.TPMEnabled' = $secData.TpmEnabled
      'security.KeyStorageDriveEnabled' = $secData.KsdEnabled
      'security.StateMigrationEncrypted' = $secData.EncryptStateAndVmMigrationTraffic
    }
  }

  $replicaData = @{}
  if ($vm.ReplicationState -ne 'Disabled' -and $null -ne $VMReplica) {
    $replicaData = [ordered]@{
      'replication.CurrentServer' = $VMReplica.CurrentReplicaServerName
      'replication.frequency' = $VMReplica.ReplicationFrequencySec
    }
  }

  $vmData = [ordered]@{
    'name' = $vm.Name
    'cluster.clustered' = $vm.IsClustered
    'runtime.host' = $vm.ComputerName
    'runtime.powerState' = Format-EnumValue $vm.State
    'runtime.operationState' = Format-EnumValue $vm.Status
    'config.vmid' = $vm.VMId
    'config.generation' = $vm.Generation
    'config.version' = $vm.Version
    'config.creationTime' = Format-DateTimeValue $vm.CreationTime
    'guest.IntegrationServicesState' = Format-EnumValue $vm.IntegrationServicesState
    'runtime.Uptime' = $vm.Uptime
    'replication.mode' = Format-EnumValue $vm.ReplicationMode
    'replication.state' = Format-EnumValue $vm.ReplicationState
    'replication.health' = Format-EnumValue $vm.ReplicationHealth
    'config.Path' = $vm.Path
    'config.ConfigurationLocation' = $vm.ConfigurationLocation
    'config.SmartPagingFilePath' = $vm.SmartPagingFilePath
    'config.SnapshotFileLocation' = $vm.SnapshotFileLocation
    'runtime.Notes' = $vm.Notes
    'config.AutomaticCriticalErrorAction' = Format-EnumValue $vm.AutomaticCriticalErrorAction
    'config.AutomaticCriticalErrorActionTimeout' = $vm.AutomaticCriticalErrorActionTimeout
    'config.AutomaticStartAction' = Format-EnumValue $vm.AutomaticStartAction
    'config.AutomaticStartDelay' = $vm.AutomaticStartDelay
    'config.AutomaticStopAction' = Format-EnumValue $vm.AutomaticStopAction
    'config.CheckPointType' = Format-EnumValue $vm.CheckPointType
  }

  foreach ($kv in $VMSec.GetEnumerator()) {
    if ($null -ne $kv.Key) {
      $vmData[$kv.Key] = $kv.Value
    }
  }

  foreach ($kv in $replicaData.GetEnumerator()) {
    if ($null -ne $kv.Key) {
      $vmData[$kv.Key] = $kv.Value
    }
  }

  foreach ($kv in $guestData.GetEnumerator()) {
    if ($null -ne $kv.Key) {
      $vmData[$kv.Key] = $kv.Value
    }
  }

  [pscustomobject]$vmData | Sort-Object -property key | ConvertTo-Json -Depth 3 -Compress
}

function Format-EnumValue {
  param([Object]$Value)

  if ($null -eq $Value) {
    return $null
  }

  return $Value.ToString()
}

function Format-DateTimeValue {
  param(
    [Object]$Value,
    [ValidateSet('Iso8601','Timestamp')][string]$Format = 'Iso8601'
  )

  if ($null -eq $Value) {
    return $null
  }

  if (-not ($Value -is [DateTime])) {
    return $Value
  }

  switch ($Format) {
    'Timestamp' { return [int64]([DateTimeOffset]$Value).ToUnixTimeMilliseconds() }
    default { return $Value.ToString('o') }
  }
}

############################################################################################################
function Get-vmCheckpoints {
  param([Object]$Checkpoints)

  if ($null -eq $Checkpoints) { 
    Write-Output("{}")
    Return
  }
  $sortedCheckpoints = @($Checkpoints | Sort-Object CreationTime)

  foreach ($checkpoint in $sortedCheckpoints) {
    [pscustomobject][ordered]@{
      'checkpoint.name' = $checkpoint.Name
      'checkpoint.created' = Format-DateTimeValue $checkpoint.CreationTime
      'checkpoint.id' = $checkpoint.Id
      'checkpoint.parentSnapshotName' = $checkpoint.ParentSnapshotName
      'checkpoint.checkpointType' = Format-EnumValue $checkpoint.CheckpointType
      'checkpoint.path' = $checkpoint.Path
    } | ConvertTo-Json -Depth 3 -Compress
  }
}

############################################################################################################
function Get-VMCPUInfo {
  param([Object]$vm, [Object]$vmProcessor)

  $vmProc = [ordered]@{
    'config.hardware.numCPU' = $vm.ProcessorCount
    'config.hardware.CompatibilityForOlderOS' = $vmProcessor.CompatibilityForOlderOperatingSystemsEnabled
    'config.hardware.CompatibilityForMigration' = $vmProcessor.CompatibilityForMigrationEnabled
    'config.hardware.HostResourceProtection' = $vmProcessor.EnableHostResourceProtection
    'config.hardware.NestedVirtualization' = $vmProcessor.ExposeVirtualizationExtensions
  }

  [pscustomobject]$vmProc | ConvertTo-Json -Depth 3 -Compress
}

############################################################################################################
function Get-VMRAMInfo {
  param([Object]$vm, [Object]$getRAMInfo)

  $RAMInfo = [ordered]@{
    'config.hardware.StartRAM' = $getRAMInfo.Startup
    'config.hardware.MinRAM' = $getRAMInfo.Minimum
    'config.hardware.MaxRAM' = $getRAMInfo.Maximum
    'config.hardware.RAMType' = $getRAMInfo.DynamicMemoryEnabled
    'config.hardware.AssignedRAM' = $vm.MemoryAssigned
    'config.hardware.RAMDemand' = $vm.MemoryDemand
  }

  [pscustomobject]$RAMInfo | ConvertTo-Json -Depth 3 -Compress
}

############################################################################################################
function Get-VMDriveInfo {
  param([Object]$vmHDDs, [Object]$vmvSANs)

  if ($null -eq $vmHDDs) { $vmHDDs = @() }
  if ($null -eq $vmvSANs) { $vmvSANs = @() }
  
  foreach ($hdd in $vmHDDs) {
    $vmHDDVHD = $null
    if ($null -ne $hdd.Path) {
      $vmHDDVHD = $hdd.Path | Get-VHD -ErrorAction SilentlyContinue
    }

    [pscustomobject][ordered]@{
      'vhd.Name' = $hdd.Name
      'vhd.ID' = $hdd.ID
      'vhd.Path' = $hdd.Path
      'vhd.controller.ID' = $hdd.ControllerId
      'vhd.controller.Type' = $hdd.ControllerType
      'vhd.controller.Location' = $hdd.ControllerLocation
      'vhd.controller.Number' = $hdd.ControllerNumber
      'vhd.Format' = Format-EnumValue $vmHDDVHD.VhdFormat
      'vhd.Type' = Format-EnumValue $vmHDDVHD.VhdType
      'vhd.DiskSize' = $vmHDDVHD.Size
      'vhd.FileSize' = $vmHDDVHD.FileSize
    } | ConvertTo-Json -Depth 3 -Compress
  }

  foreach ($san in $vmvSANs) {
    [pscustomobject][ordered]@{
      'vasn.Name' = $san.SanName
      'vasn.WorldWideNodeNameSetA' = $san.WorldWideNodeNameSetA
      'vasn.WorldWidePortNameSetA' = $san.WorldWidePortNameSetA
      'vasn.WorldWideNodeNameSetB' = $san.WorldWideNodeNameSetB
      'vasn.WorldWidePortNameSetB' = $san.WorldWidePortNameSetB
      'vasn.ID' = $san.ID
    } | ConvertTo-Json -Depth 3 -Compress
  }
}

############################################################################################################
function Get-VMNICInfo {
  param([Object]$vmNetCards)

  if ($null -eq $vmNetCards) { $vmNetCards = @() }
  
  foreach ($nic in $vmNetCards) {
    $vlanSetting = @{}
    if ($null -ne $nic.VlanSetting) {
      $vlandata = $nic.VlanSetting | Select-Object OperationMode, AccessVlanId
      $vlanSetting = [ordered]@{
        'nic.VLAN.mode' = Format-EnumValue $vlandata.OperationMode
        'nic.VLAN.id' = $vlandata.AccessVlanId
      }
    }

    $nicData = [ordered]@{
      'nic.security.RouterGuard' = $nic.RouterGuard
      'nic.security.DHCPGuard' = $nic.DHCPGuard
      'nic.BandwidthSetting' = $nic.BandwidthSetting
      'nic.dynamicMAC' = $nic.DynamicMACAddressEnabled
      'nic.MAC' = $nic.MacAddress
      'nic.IPAddresses' = $nic.IPAddresses
      'nic.vswitch' = $nic.SwitchName
      'nic.connectionstate' = $nic.Connected
      'nic.id' = $nic.ID
      'nic.name' = $nic.Name
    }
    
    foreach ($kv in $vlanSetting.GetEnumerator()) {
      if ($null -ne $kv.Key) {
        $nicData[$kv.Key] = $kv.Value
      }
    }
    [pscustomobject]$nicData | ConvertTo-Json -Depth 3 -Compress
  }
}

############################################################################################################
function Get-VMISInfo {
  param([Object]$vmIntSer)

  if ($null -eq $vmIntSer) { $vmIntSer = @() }
  
  foreach ($service in $vmIntSer) {
    [pscustomobject][ordered]@{
      'enabled' = $service.Enabled
      'name' = $service.Name
      'PrimaryStatusDescription' = $service.PrimaryStatusDescription
      'SecondaryStatusDescription' = $service.SecondaryStatusDescription
    } | ConvertTo-Json -Depth 2 -Compress
  }
}

############################################################################################################
function Get-VMInventoryHost() {
  if ($null -eq (Get-Command Get-VM -ErrorAction SilentlyContinue)) {
    '<<<hyperv_node_json:sep(0)>>>'
    [ordered]@{ error = 'Hyper-V cmdlets are not available on this host.' } | ConvertTo-Json -Depth 1
    return
  }

  if ($null -ne (Get-Command Get-WindowsOptionalFeature -ErrorAction SilentlyContinue)) {
    if ((Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -ErrorAction SilentlyContinue).State -ne 'Enabled') {
      '<<<hyperv_node_json:sep(0)>>>'
      [ordered]@{ error = 'Hyper-V feature is not enabled. Exiting.' } | ConvertTo-Json -Depth 1
      return
    }
  }

  '<<<hyperv_node_json:sep(0)>>>'
  $vms = @(Get-VM | Sort-Object Name)
  $hasVMSecurity = $null -ne (Get-Command Get-VMSecurity -ErrorAction SilentlyContinue)

  $payload = [ordered]@{
    host = $env:COMPUTERNAME
    vmCount = $vms.Count
  }
  $payload | ConvertTo-Json -Depth 3 -Compress
  if ($vms.Count -eq 0) {
    return
  }

  # --- BULK FETCHING WITH PIPELINE ---
  $allProcessors = $vms | Get-VMProcessor | Group-Object { $_.VMId.Guid } -AsHashTable -AsString
  $allMemories   = $vms | Get-VMMemory    | Group-Object { $_.VMId.Guid } -AsHashTable -AsString
  $allHDDs       = $vms | Get-VMHardDiskDrive | Group-Object { $_.VMId.Guid } -AsHashTable -AsString
  $allVSANs      = $vms | Get-VMFibreChannelHba -ErrorAction SilentlyContinue | Group-Object { $_.VMId.Guid } -AsHashTable -AsString
  $allNICs       = $vms | Get-VMNetworkAdapter | Group-Object { $_.VMId.Guid } -AsHashTable -AsString
  $allIS         = $vms | Get-VMIntegrationService | Group-Object { $_.VMId.Guid } -AsHashTable -AsString
  $allSnaps      = $vms | Get-VMSnapshot | Group-Object { $_.VMId.Guid } -AsHashTable -AsString
  $allReplicas   = $vms | Get-VMReplication -ErrorAction SilentlyContinue | Group-Object { $_.VMId.Guid } -AsHashTable -AsString

  # --- NULL-ARRAY PROTECTION ---
  if ($null -eq $allProcessors) { $allProcessors = @{} }
  if ($null -eq $allMemories)   { $allMemories   = @{} }
  if ($null -eq $allHDDs)       { $allHDDs       = @{} }
  if ($null -eq $allVSANs)      { $allVSANs      = @{} }
  if ($null -eq $allNICs)       { $allNICs       = @{} }
  if ($null -eq $allIS)         { $allIS         = @{} }
  if ($null -eq $allSnaps)      { $allSnaps      = @{} }
  if ($null -eq $allReplicas)   { $allReplicas   = @{} }

  foreach ($vm in $vms) {
    $vmIdString = $vm.VMId.Guid
    Write-Output('<<<<' + $vm.Name + '>>>>')
    Write-Output("<<<hyperv_vm_general_json:sep(0)>>>")
    Get-VMGeneralInfo -vm $vm -vmReplica ($allReplicas[$vmIdString] | Select-Object -First 1) -HasVMSecurity $hasVMSecurity
    Write-Output("<<<hyperv_vm_checkpoints_json:sep(0)>>>")
    Get-vmCheckpoints -Checkpoints $allSnaps[$vmIdString]
    Write-Output("<<<hyperv_vm_cpu_json:sep(0)>>>")
    Get-VMCPUInfo -vm $vm -vmProcessor ($allProcessors[$vmIdString] | Select-Object -First 1)
    Write-Output("<<<hyperv_vm_ram_json:sep(0)>>>")
    Get-VMRAMInfo -vm $vm -getRAMInfo ($allMemories[$vmIdString] | Select-Object -First 1)
    Write-Output("<<<hyperv_vm_nic_json:sep(0)>>>")
    Get-VMNICInfo -vmNetCards $allNICs[$vmIdString]
    Write-Output("<<<hyperv_vm_integration_json:sep(0)>>>")
    Get-VMISInfo -vmIntSer $allIS[$vmIdString]
    Write-Output("<<<hyperv_vm_vhd_json:sep(0)>>>")
    Get-VMDriveInfo -vmHDDs $allHDDs[$vmIdString] -vmvSANs $allVSANs[$vmIdString]
    Write-Output("<<<<>>>>")
  }
}

Get-VMInventoryHost

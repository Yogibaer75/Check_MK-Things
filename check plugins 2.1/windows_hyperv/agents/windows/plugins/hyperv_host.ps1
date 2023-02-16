function Get-VMGeneralInfo {
  param
  (
    [Object]
    $vm,

    [Object]
    $clusterNode
  )

  Write-Host 'name' ($vm.Name)
  Write-Host 'cluster.clustered' ($vm.IsClustered)
  if ($vm.IsClustered) {
    $VMClusterResource = (Get-ClusterResource -VMId $vm.VMId)
    Write-Host 'cluster.group' $VMClusterResource.OwnerGroup
    Write-Host 'cluster.startup_priority' $VMClusterResource.OwnerGroup.Priority
  }
  Write-Host 'runtime.host' ($vm.ComputerName)
  Write-Host 'runtime.powerState' ($vm.State)
  Write-Host 'runtime.operationState' ($vm.Status)
  Write-Host 'config.vmid' ($vm.VMId)
  Write-Host 'config.generation' ($vm.Generation)
  Write-Host 'config.version' ($vm.Version)
  Write-Host 'config.created' ($vm.CreationTime)
  if ($null -ne $vm.Groups) {
    Write-Host 'config.MemberOfVMGroups' $vm.Groups.Count
    foreach ($Member in $vm.Groups) {
      Write-Host $null ($vm.Groups.Name + ' (' + $vm.Groups.InstanceId + ')')
    }
  }
  Write-Host 'guest.fqdn' (Get-VMKVPdata -vm $vm.Name -clusterNode $clusterNode -kvpAttribute 'FullyQualifiedDomainName')
  Write-Host 'guest.os' (Get-VMKVPdata -vm $vm.Name -clusterNode $clusterNode -kvpAttribute 'OSName')
  Write-Host 'guest.IntegrationServicesVersion' (Get-VMKVPdata -vm $vm.Name -clusterNode $clusterNode -kvpAttribute 'IntegrationServicesVersion')
  Write-Host 'guest.IntegrationServicesState' ($vm.IntegrationServicesState)
  Write-Host 'config.AutomaticStopAction' ($vm.AutomaticStopAction)
  Write-Host 'config.AutomaticStartAction' ($vm.AutomaticStartAction)
  Write-Host 'config.AutomaticStartDelay' ($vm.AutomaticStartDelay)
  Write-Host 'config.ConfigurationPath' ($vm.ConfigurationLocation)
  Write-Host 'config.CheckpointPath' ($vm.SnapshotFileLocation)
  $CheckpointType = $vm.CheckpointType
  if ($null -eq $CheckpointType) {
    $CheckpointType = 'Standard_(legacy)'
  }
  Write-Host 'config.CurrentCheckpointType' ($CheckpointType)
  $VMReplica = Get-VMReplication -ComputerName $clusterNode -VMName $vm.Name -ErrorAction SilentlyContinue
  If ($null -ne $VMReplica) {
    Write-Host 'replication.mode' ($VMReplica.ReplicationMode)
    Write-Host 'replication.state' ($VMReplica.ReplicationState)
    Write-Host 'replication.CurrentServer' ($VMReplica.CurrentReplicaServerName)
    Try {
      $ReplicationFreq = ($VMReplica.ReplicationFrequencySec)
    }
    Catch {
      $ReplicationFreq = $null
    }
    If ($null -ne $ReplicationFreq) {
      Write-Host 'replication.frequency' $ReplicationFreq
    }
  }
  else {
    Write-Host 'replication.mode' 'not configured'
  }

  $VMConnect = Get-VMConnectAccess -ComputerName $clusterNode -VMName $vm.Name
  if ($VMConnect.Count -eq 0) {
    $VMConnectUsers = 'nobody'
  }
  else {
    $VMConnectUsers = $VMConnect.Username # -join ', '
  }
  Write-Host 'access' $VMConnectUsers

  if ($null -ne (Get-Command Get-VMSecurity -ErrorAction SilentlyContinue)) {
  
    $VMSec = (Get-VMSecurity -VM $vm)
    Write-Host 'security.shieldedVM' $VMSec.Shielded
    Write-Host 'security.TPMEnabled' $VMSec.TpmEnabled
    Write-Host 'security.KeyStorageDriveEnabled' $VMSec.KsdEnabled
    Write-Host 'security.StateMigrationEncrypted' $VMSec.EncryptStateAndVmMigrationTraffic
  }
}

############################################################################################################

function Get-vmCheckpoints {
  param
  (
    [Object]
    $vm,

    [Object]
    $clusterNode
  )

  $Checkpoints = (Get-VMSnapshot -VMName $vm.Name -ComputerName $clusterNode | Sort-Object CreationTime)
  Write-Host ('checkpoints ' + $Checkpoints.Length)
  if ($Checkpoints.Length -eq 0) {
    Write-Host $null 'none'
  }
  else {
    foreach ($Checkpoint in $Checkpoints) {
      Write-Host 'checkpoint.name' ($Checkpoint.Name)
      Write-Host 'checkpoint.path' ($Checkpoint.Path)
      Write-Host 'checkpoint.created' ($Checkpoint.CreationTime)
      Write-Host 'checkpoint.parent' ($Checkpoint.ParentSnapshotName)
    
    }
  }
}

############################################################################################################

function Get-VMCPUInfo {
  param
  (
    [Object]
    $vm,

    [Object]
    $clusterNode
  )


  Write-Host 'config.hardware.numCPU' ($vm.ProcessorCount)
  $vmProcessor = Get-VMProcessor -VMName $vm.Name -ComputerName $clusterNode
  Write-Host 'config.hardware.CompatibilityForOlderOS' ($vmProcessor.CompatibilityForOlderOperatingSystemsEnabled)
  Write-Host 'config.hardware.CompatibilityForMigration' ($vmProcessor.CompatibilityForMigrationEnabled)
  if ($null -ne $vmProcessor.EnableHostResourceProtection) {
    Write-Host 'config.hardware.HostResourceProtection' ($vmProcessor.EnableHostResourceProtection)
  }
  if ($null -ne $vmProcessor.ExposeVirtualizationExtensions) {
    Write-Host 'config.hardware.NestedVirtualization' ($vmProcessor.ExposeVirtualizationExtensions)
  }

}

############################################################################################################
function Get-VMRAMInfo {
  param
  (
    [Object]
    $vm,

    [Object]
    $clusterNode
  )


  $getRAMInfo = Get-VMMemory -VMName $vm.Name -ComputerName $clusterNode
  if ($getRAMInfo.DynamicMemoryEnabled -eq $true) {
    Write-Host 'config.hardware.RAMType' 'Dynamic Memory'
    Write-Host 'config.hardware.StartRAM' ([string]($getRAMInfo.Startup / 1MB))
    Write-Host 'config.hardware.MinRAM' ([string]($getRAMInfo.Minimum / 1MB))
    Write-Host 'config.hardware.MaxRAM' ([string]($getRAMInfo.Maximum / 1MB))
  }
  else {
    Write-Host 'config.hardware.RAMType' 'Static Memory'
    Write-Host 'config.hardware.RAM' ([string]($vm.MemoryStartup / 1MB))
  }

}

############################################################################################################
function Get-VMDriveInfo {
  param
  (
    [Object]
    $vm,

    [Object]
    $clusterNode
  )

  $vmHDDs = (Get-VMHardDiskDrive -VMName $vm.Name -ComputerName $clusterNode | Sort-Object Name)


  Write-Host 'vhd' ($vmHDDs.Count)
      
  ForEach ($vmHDD in $vmHDDs) {
  
    Write-Host 'vhd.name' ($vmHDD.Name)
    Write-Host 'vhd.controller.id' ($vmHDD.ID)
    Write-Host 'vhd.controller.type' ($vmHDD.ControllerType)
    Write-Host 'vhd.controller.number' ($vmHDD.ControllerNumber)
    Write-Host 'vhd.controller.location' ($vmHDD.ControllerLocation)
    Write-Host 'vhd.path' ($vmHDD.Path)
    $vmHDDVHD = $vmHDD.Path | Get-VHD -ComputerName $clusterNode -ErrorAction SilentlyContinue
    if ($null -ne $vmHDDVHD) {
      Write-Host 'vhd.format' ($vmHDDVHD.VhdFormat)
      Write-Host 'vhd.type' ($vmHDDVHD.VhdType)
      Write-Host 'vhd.maximumcapacity' ($vmHDDVHD.Size / 1MB)
      Write-Host 'vhd.usedcapacity' ($vmHDDVHD.FileSize / 1MB)
    }
    else {
      Write-Host 'vhd.type' 'Direct'
    }
  }

  # Get vFC, if any
  $vmvSAN = (Get-VMFibreChannelHba -VMName $vm.Name -ComputerName $clusterNode | Sort-Object Name)
  if ($null -ne $vmvSAN) {
  
    Write-Host 'vsan' ($vmvSAN.Count)
      
    ForEach ($vmvSAN in $vmvSAN) {
    
      Write-Host 'vsan.name' ($vmvSAN.SanName)
      Write-Host 'vsan.primaryWWNN' ($vmvSAN.WorldWideNodeNameSetA)
      Write-Host 'vsan.primaryWWPN' ($vmvSAN.WorldWidePortNameSetA)
      Write-Host 'vsan.secondaryWWNN' ($vmvSAN.WorldWideNodeNameSetB)
      Write-Host 'vsan.secondaryWWPN' ($vmvSAN.WorldWidePortNameSetB)
      Write-Host 'vsan.id' ($vmvSAN.ID)
    }
  }
}

############################################################################################################
function Get-VMNICInfo {
  param
  (
    [Object]
    $vm,

    [Object]
    $clusterNode
  )

  $vmNetCards = (Get-VMNetworkAdapter -VMName $vm.Name -ComputerName $clusterNode | Sort-Object Name, ID)

  Write-Host 'nic' ($vmNetCards.Count)
  ForEach ($vmNetCard in $vmNetCards) {
  
    Write-Host 'nic.name' ($vmNetCard.Name)
    Write-Host 'nic.id' ($vmNetCard.ID)
    Write-Host 'nic.connectionstate' ($vmNetCard.Connected)

    #vmNetCard Switch
    if ($vmNetCard.SwitchName.Length -ne 0) {
      Write-Host 'nic.vswitch' ($vmNetCard.SwitchName)
    }
    else {
      Write-Host 'nic.vswitch' 'none'
    }

    #vmNetCard MACAddress
    Write-Host 'nic.dynamicMAC' ($vmNetCard.DynamicMacAddressEnabled)
    if ($vmNetCard.MacAddress.Length -ne 0) {
      Write-Host 'nic.MAC' ($vmNetCard.MacAddress)
    }
    else {
      Write-Host 'nic.MAC' 'not assigned'
    }

    #vmNetCard IPAddress
    $vmnetCardIPs = $vmNetCard.IPAddresses
    if ($vmNetCard.IPAddresses.Length -ne 0) {
      ForEach ($vmnetCardIP in $vmnetCardIPs) {
        Write-Host 'nic.IP' ($vmNetCardIP)
      }
    }
    else {
      Write-Host 'nic.IP' 'not assigned'
    }
    # special features (could be extended in future versions)
    Write-Host 'nic.security.DHCPGuard' ($vmNetCard.DhcpGuard)
    Write-Host 'nic.security.RouterGuard' ($vmNetCard.RouterGuard)
    Write-Host 'nic.VLAN.mode' ($vmNetCard.VlanSetting.OperationMode)
    Write-Host 'nic.VLAN.id' ($vmNetCard.VlanSetting.AccessVlanId)
    if ($null -ne $vmNetCard.BandwidthSetting.MinimumBandwidthAbsolute -or $null -ne $vmNetCard.BandwidthSetting.MaximumBandwidth) {
      # Bandwidth settings say they use Mbit but they only multiply the GUI value by a million ...
      Write-Host 'nic.bandwidth.min' ($vmNetCard.BandwidthSetting.MinimumBandwidthAbsolute)
      Write-Host 'nic.bandwidth.max' ($vmNetCard.BandwidthSetting.MaximumBandwidth)
    }
  }
}

############################################################################################################
function Get-VMISInfo {
  param
  (
    [Object]
    $vm,

    [Object]
    $clusterNode
  )


  $vmIntSer = (Get-VMIntegrationService -VMName $vm.Name -ComputerName $clusterNode | Sort-Object Name)
  Write-Host 'guest.tools.number' ($vmIntSer.Count)
  foreach ($IS in $vmIntSer) {
    if ($IS.Enabled) {
      $ISActive = 'active'
    }
    else {
      $ISActive = 'inactive'
    }
    Write-Host ('guest.tools.service.' + $IS.Name.replace(' ' , '_')) $ISActive
  }      

}

############################################################################################################
function Get-VMKVPdata {
  param
  (
    [Object]
    $vm,

    [Object]
    $clusterNode,

    [Object]
    $kvpAttribute
  )

  $WMIFilter = "ElementName='$vm'"
  $attrName = "/INSTANCE/PROPERTY[@NAME='Name']/VALUE[child::text()='$kvpAttribute']"
  $VMWMI = Get-WmiObject -Namespace root\virtualization\v2 -Class Msvm_ComputerSystem -Filter $WMIFilter -ComputerName $clusterNode -ErrorAction SilentlyContinue
  Try {
    $VMWMI.GetRelated('Msvm_KvpExchangeComponent').GuestIntrinsicExchangeItems | ForEach-Object { `
        $GuestExchangeItemXml = ([XML]$_).SelectSingleNode(`
          $attrName)
       
      if ($null -ne $GuestExchangeItemXml) {
        $script:VMKVPdata = ($GuestExchangeItemXml.SelectSingleNode(`
              "/INSTANCE/PROPERTY[@NAME='Data']/VALUE/child::text()").Value)
      }   
    }
  }
  Catch {
    # this error handling is ugly - feel free to give me a hint ...
  }
  return $VMKVPData
}

############################################################################################################

function Get-VMInventoryHost() {
  param
  (
    [Parameter(Mandatory = $false, Position = 1)]
    [string]$Node
  )

  # creates an inventory reports of all VMs on a single host

  if ($Node.Length -eq 0) {
    '<<<hyperv_node>>>'
    Return
  }

  # connect only if host reacts to ping
  '<<<hyperv_node>>>'
  if (Test-Connection -ComputerName $Node -Quiet) {
    $vms = (Get-VM -ComputerName $Node | Sort-Object Name)
    Write-Host 'vms.defined' $vms.count
    foreach ($vm in $vms) {
      '<<<<' + $vm.Name + '>>>>'
      '<<<hyperv_vm_general>>>'
      Get-VMGeneralInfo -vm $vm -clusterNode $Node
      '<<<hyperv_vm_checkpoints>>>'
      Get-vmCheckpoints -vm $vm -clusterNode $Node
      '<<<hyperv_vm_cpu>>>'
      Get-VMCPUInfo -vm $vm -clusterNode $Node
      '<<<hyperv_vm_ram>>>'
      Get-VMRAMInfo -vm $vm -clusterNode $Node
      '<<<hyperv_vm_vhd>>>'
      Get-VMDriveInfo -vm $vm -clusterNode $Node
      '<<<hyperv_vm_nic>>>'
      Get-VMNICInfo -vm $vm -clusterNode $Node
      '<<<hyperv_vm_integration>>>'
      Get-VMISInfo -vm $vm -clusterNode $Node
      '<<<<>>>>'
    }

  }
  else {
    '<<<hyperv_node>>>'
    Return
  }
}

Get-VMInventoryHost ($env:COMPUTERNAME)

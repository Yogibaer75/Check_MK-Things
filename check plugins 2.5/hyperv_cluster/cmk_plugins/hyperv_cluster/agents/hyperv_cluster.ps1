# Reports the state of a Windows failover cluster: the cluster itself, its nodes,
# networks, disks, cluster shared volumes and clustered virtual machines.
# Every node of the cluster reports the same data.

### common powershell header for all checkmk windows agents plugins
$pshost = Get-Host
$pswindow = $pshost.UI.RawUI

$newsize = $pswindow.BufferSize
$newsize.height = 300
$newsize.width = 200
$pswindow.buffersize = $newsize

$newsize = $pswindow.windowsize
$newsize.width = 200
$pswindow.windowsize = $newsize

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($true)

function Get-ClusterInfo() {
    # Nothing to report on hosts without the failover cluster cmdlets or outside a cluster
    if (-not (Get-Command Get-Cluster -ErrorAction SilentlyContinue)) {
        return
    }
    $cluster = Get-Cluster -ErrorAction SilentlyContinue
    if ($null -eq $cluster) {
        return
    }

    Write-Host('<<<hyperv_cluster_general>>>')
    Write-Host 'cluster.name' $cluster.Name

    $clusterGroup = Get-ClusterGroup | Where-Object { $_.GroupType -eq 'Cluster' }
    $clusterIPResource = Get-ClusterResource | Where-Object { $_.ResourceType -eq 'IP Address' -and $_.OwnerGroup -eq $clusterGroup }
    $clusterIP = $clusterIPResource | Get-ClusterParameter Address
    $clusterSubnet = $clusterIPResource | Get-ClusterParameter SubnetMask
    # Clusters with several IP addresses, e.g. dual-stack or multi-subnet clusters
    Write-Host 'cluster.ip' (@($clusterIP.Value) -join ', ')
    Write-Host 'cluster.subnet' (@($clusterSubnet.Value) -join ', ')

    $quorum = Get-ClusterQuorum
    Write-Host 'quorum.resourcename' ($quorum.QuorumResource.Name)
    Write-Host 'quorum.type' ($quorum.QuorumType)

    Write-Host('<<<hyperv_cluster_nodes>>>')
    $clusterNodes = @(Get-ClusterNode | Sort-Object ID)
    Write-Host 'cluster.number_of_nodes' ($clusterNodes.Count)
    foreach ($clusterNode in $clusterNodes) {
        Write-Host 'cluster.node.name' ($clusterNode.Name)
        Write-Host 'cluster.node.id' ($clusterNode.ID)
        Write-Host 'cluster.node.state' ($clusterNode.State)
        Write-Host 'cluster.node.info' ($clusterNode.StatusInformation)
        Write-Host 'cluster.node.weight' ($clusterNode.NodeWeight)
        Write-Host 'cluster.node_vendor.manufacturer' ($clusterNode.Manufacturer)
        Write-Host 'cluster.node_vendor.model' ($clusterNode.Model)
        Write-Host 'cluster.node_vendor.serial' ($clusterNode.SerialNumber)
    }

    Write-Host('<<<hyperv_cluster_network>>>')
    $clusterNetworks = @(Get-ClusterNetwork | Sort-Object Name)
    Write-Host 'cluster.number_of_networks' ($clusterNetworks.Count)
    foreach ($clusterNetwork in $clusterNetworks) {
        Write-Host 'cluster.network.name' ($clusterNetwork.Name)
        Write-Host 'cluster.network.role' ([string]$clusterNetwork.Role)
        Write-Host 'cluster.network.state' ($clusterNetwork.State)
        Write-Host 'cluster.network.ip' ($clusterNetwork.Address)
        Write-Host 'cluster.network.netmask' ($clusterNetwork.Addressmask)
        Write-Host 'cluster.network.ipv4_address' ($clusterNetwork.Ipv4Addresses)
        Write-Host 'cluster.network.ipv6_address' ($clusterNetwork.Ipv6Addresses)
    }

    Write-Host('<<<hyperv_cluster_disks>>>')
    $clusterDisks = @(Get-ClusterResource | Where-Object { $_.ResourceType -eq 'Physical Disk' } | Sort-Object OwnerGroup, Name)
    Write-Host 'cluster.number_of_disks' ($clusterDisks.Count)
    foreach ($disk in $clusterDisks) {
        Write-Host 'cluster.disk.name' ($disk.Name)
        Write-Host 'cluster.disk.owner_group' ($disk.OwnerGroup)
        Write-Host 'cluster.disk.owner_node' ($disk.OwnerNode)
        Write-Host 'cluster.disk.state' ($disk.State)
    }

    Write-Host('<<<hyperv_cluster_csv>>>')
    $clusterSharedVolumes = @(Get-ClusterSharedVolume -Cluster $cluster | Sort-Object Name)
    Write-Host 'cluster.number_of_csv' ($clusterSharedVolumes.Count)
    foreach ($csv in $clusterSharedVolumes) {
        Write-Host 'cluster.csv.name' ($csv.Name)
        Write-Host 'cluster.csv.owner' ($csv.OwnerNode)
        foreach ($csvInfo in $csv.SharedVolumeInfo) {
            Write-Host 'cluster.csv.volume' ($csvInfo.FriendlyVolumeName)
            $partition = $csvInfo.Partition
            Write-Host 'cluster.csv.size' ($partition.Size)
            Write-Host 'cluster.csv.free_space' ($partition.FreeSpace)
            Write-Host 'cluster.csv.used_space' ($partition.UsedSpace)
        }
    }

    Write-Host('<<<hyperv_cluster_roles>>>')
    $clusterVMs = @(Get-ClusterGroup -Cluster $cluster | Where-Object { $_.GroupType -eq 'VirtualMachine' } | Sort-Object Name)
    if ($clusterVMs.Count -ne 0) {
        Write-Host 'cluster.number_of_vms' ($clusterVMs.Count)
        foreach ($clusterVM in $clusterVMs) {
            Write-Host 'cluster.vm.name' ($clusterVM.Name)
            Write-Host 'cluster.vm.state' ($clusterVM.State)
            Write-Host 'cluster.vm.owner' ($clusterVM.OwnerNode)
        }
    }
}

Get-ClusterInfo

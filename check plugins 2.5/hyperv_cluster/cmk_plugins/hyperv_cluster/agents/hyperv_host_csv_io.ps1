# Reports disk IO counters of the cluster shared volumes (CSV) as seen from this node.
# Volumes owned by this node go to hyperv_host_io_local, all others to hyperv_host_io_remote.
# Each line reads "<CSV name>\<counter name> <value>".

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

if (-not (Get-Command Get-ClusterSharedVolume -ErrorAction SilentlyContinue)) {
    exit 0
}

# The formatted performance data truncates latencies and queue lengths to whole numbers.
# Read the raw counters twice and compute the values like Windows does for each counter type.
# The CIM property names do not depend on the system language. Map them to the English
# counter names the check expects.
$rateCounters = [ordered]@{
    "DiskReadsPersec"      = "disk reads/sec"
    "DiskWritesPersec"     = "disk writes/sec"
    "DiskReadBytesPersec"  = "disk read bytes/sec"
    "DiskWriteBytesPersec" = "disk write bytes/sec"
}
$queueLengthCounters = [ordered]@{
    "AvgDiskReadQueueLength"  = "avg. disk read queue length"
    "AvgDiskWriteQueueLength" = "avg. disk write queue length"
}
$averageTimerCounters = [ordered]@{
    "AvgDisksecPerRead"  = "avg. disk sec/read"
    "AvgDisksecPerWrite" = "avg. disk sec/write"
}

# The CIM instance name is "<disk number> <drive letters>", for example "0 C:", or just "1".
function Get-RawDiskCounters {
    $countersByDisk = @{}
    foreach ($rawDisk in (Get-CimInstance -ClassName Win32_PerfRawData_PerfDisk_PhysicalDisk | Where-Object Name -ne "_Total")) {
        $countersByDisk[[int]($rawDisk.Name -split ' ')[0]] = $rawDisk
    }
    return $countersByDisk
}

# Some raw counters are 32 bit values that wrap around.
function Get-Delta($first, $second) {
    $delta = [decimal]$second - [decimal]$first
    if ($delta -lt 0) {
        $delta += [decimal]4294967296
    }
    return $delta
}

function Get-Ratio([decimal]$numerator, [decimal]$denominator) {
    if ($denominator -le 0) {
        return [decimal]0
    }
    return $numerator / $denominator
}

function Format-Value([decimal]$value) {
    return $value.ToString([System.Globalization.CultureInfo]::InvariantCulture)
}

$clusterSharedVolumes = @(Get-ClusterSharedVolume -ErrorAction SilentlyContinue)

$disksByGuid = @{}
foreach ($disk in Get-Disk) {
    if ($disk.Guid) {
        $disksByGuid[$disk.Guid.Trim('{}')] = $disk
    }
}

$firstSample = Get-RawDiskCounters
Start-Sleep -Seconds 1
$secondSample = Get-RawDiskCounters

$localLines = @()
$remoteLines = @()
foreach ($csv in $clusterSharedVolumes) {
    $diskGuid = ($csv | Get-ClusterParameter DiskIdGuid).Value
    if (-not $diskGuid) {
        continue
    }
    $disk = $disksByGuid[$diskGuid.Trim('{}')]
    if ($null -eq $disk) {
        continue
    }
    $first = $firstSample[[int]$disk.Number]
    $second = $secondSample[[int]$disk.Number]
    if ($null -eq $first -or $null -eq $second) {
        continue
    }

    $frequency = [decimal]$second.Frequency_PerfTime
    $seconds = Get-Ratio (Get-Delta $first.Timestamp_PerfTime $second.Timestamp_PerfTime) $frequency
    $ticks100ns = Get-Delta $first.Timestamp_Sys100NS $second.Timestamp_Sys100NS

    $lines = @()
    # PERF_COUNTER_COUNTER and PERF_COUNTER_BULK_COUNT: events per second
    foreach ($property in $rateCounters.Keys) {
        $value = Get-Ratio (Get-Delta $first.$property $second.$property) $seconds
        $lines += "{0}\{1} {2}" -f $csv.Name, $rateCounters[$property], (Format-Value $value)
    }
    # PERF_COUNTER_100NS_QUEUELEN_TYPE: average queue length
    foreach ($property in $queueLengthCounters.Keys) {
        $value = Get-Ratio (Get-Delta $first.$property $second.$property) $ticks100ns
        $lines += "{0}\{1} {2}" -f $csv.Name, $queueLengthCounters[$property], (Format-Value $value)
    }
    # PERF_AVERAGE_TIMER: seconds per operation
    foreach ($property in $averageTimerCounters.Keys) {
        $base = "{0}_Base" -f $property
        $elapsed = Get-Ratio (Get-Delta $first.$property $second.$property) $frequency
        $value = Get-Ratio $elapsed (Get-Delta $first.$base $second.$base)
        $lines += "{0}\{1} {2}" -f $csv.Name, $averageTimerCounters[$property], (Format-Value $value)
    }

    if ($csv.OwnerNode.Name -eq $env:COMPUTERNAME) {
        $localLines += $lines
    }
    else {
        $remoteLines += $lines
    }
}

Write-Host("<<<hyperv_host_io_local>>>")
$localLines | ForEach-Object { Write-Host $_ }

Write-Host("<<<hyperv_host_io_remote>>>")
$remoteLines | ForEach-Object { Write-Host $_ }

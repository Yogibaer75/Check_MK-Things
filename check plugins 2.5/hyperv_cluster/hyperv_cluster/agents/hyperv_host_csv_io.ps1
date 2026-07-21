### common powershell header for all checkmk windows agents plugins
$pshost = Get-Host              # Get the PowerShell Host.
$pswindow = $pshost.UI.RawUI    # Get the PowerShell Host's UI.

$newsize = $pswindow.BufferSize # Get the UI's current Buffer Size.
$newsize.height = 300           # Set the new buffer's heigt to 300 lines.
$newsize.width = 200            # Set the new buffer's width to 200 columns.
$pswindow.buffersize = $newsize # Set the new Buffer Size as active.

$newsize = $pswindow.windowsize # Get the UI's current Window Size.
$newsize.width = 200            # Set the new Window Width to 200 columns.
$pswindow.windowsize = $newsize # Set the new Window Size as active.

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($true)

###

Write-Host("<<<hyperv_host_io_local>>>")

# MAPPING: Sprachunabhängige WMI-Properties -> Checkmk Englische Counter-Namen
$counterMap = [ordered]@{
    "CurrentDiskQueueLength"  = "Current Disk Queue Length"
    "PercentDiskTime"         = "% Disk Time"
    "AvgDiskQueueLength"      = "Avg. Disk Queue Length"
    "PercentDiskReadTime"     = "% Disk Read Time"
    "AvgDiskReadQueueLength"  = "Avg. Disk Read Queue Length"
    "PercentDiskWriteTime"    = "% Disk Write Time"
    "AvgDiskWriteQueueLength" = "Avg. Disk Write Queue Length"
    "AvgDisksecPerTransfer"   = "Avg. Disk sec/Transfer"
    "AvgDisksecPerRead"       = "Avg. Disk sec/Read"
    "AvgDisksecPerWrite"      = "Avg. Disk sec/Write"
    "DiskTransfersPersec"     = "Disk Transfers/sec"
    "DiskReadsPersec"         = "Disk Reads/sec"
    "DiskWritesPersec"        = "Disk Writes/sec"
    "DiskBytesPersec"         = "Disk Bytes/sec"
    "DiskReadBytesPersec"     = "Disk Read Bytes/sec"
    "DiskWriteBytesPersec"    = "Disk Write Bytes/sec"
    "AvgDiskBytesPerTransfer" = "Avg. Disk Bytes/Transfer"
    "AvgDiskBytesPerRead"     = "Avg. Disk Bytes/Read"
    "AvgDiskBytesPerWrite"    = "Avg. Disk Bytes/Write"
    "PercentIdleTime"         = "% Idle Time"
    "SplitIOPerSec"           = "Split IO/Sec"
}

$customobjects = @()
$hostname = $env:COMPUTERNAME.ToLower()

# Abrufen der Performance-Daten über CIM (garantiert sprachunabhängig)
$perfDisks = Get-CimInstance -ClassName Win32_PerfFormattedData_PerfDisk_PhysicalDisk | Where-Object Name -ne "_Total"

foreach ($disk in $perfDisks) {
    # Der CIM-Name ist meist "0 C:" oder nur "1". Wir extrahieren nur die Zahl für die Regex.
    $diskNumber = ($disk.Name -split ' ')[0] 
    
    foreach ($prop in $counterMap.Keys) {
        $englishName = $counterMap[$prop]
        
        # Pfad exakt so nachbauen, wie Get-Counter ihn früher geliefert hat.
        # Wichtig: .ToLower() stellt sicher, dass die Regex des originalen Skripts weiterhin greift.
        $path = "\\$hostname\physicaldisk($diskNumber)\$englishName".ToLower()
        
        $customobjects += [pscustomobject]@{
            Path  = $path
            Value = $disk.$prop
        }
    }
}

$counts = @()
$remotecounts = @()
$idtolun = @{}

$csvs = Get-ClusterSharedVolume
foreach ( $csv in $csvs )
    {
    if ($csv | Where-Object {$_.OwnerNode -match $env:COMPUTERNAME})
        {
        $diskguid = ($csv | Get-ClusterParameter DiskIdGuid).Value
        $lunid = $csv.Name
        $disk = get-disk | Where-Object {$_.guid -match $diskguid}
        $diskid = $disk.DiskNumber
        $idtolun[$diskid] = $lunid
        $counts +=  $disk
        }
    else {
        $diskguid = ($csv | Get-ClusterParameter DiskIdGuid).Value
        $lunid = $csv.Name
        $disk = get-disk | Where-Object {$_.guid -match $diskguid}
        $diskid = $disk.DiskNumber
        $idtolun[$diskid] = $lunid
        $remotecounts +=  $disk
        }
    }

$resultlist = @()

foreach ( $volume in $counts) {
    foreach ( $element in $customobjects) {
        $checkString = $volume.Number
        if ($element.Path -match "\($checkString\)") {
            $element.Path = [regex]::Replace($element.Path, '\\\\.*\\physicaldisk\(.*\)\\',$idtolun[$checkString]+'\')
            $resultlist += $element
        }
    }
}

$resultlist | Select-Object Path, Value | ForEach-Object {
    $_.Path = [regex]::Replace($_.Path, "\\\\$hostname\\physicaldisk\([0-9]+\)","");
    $_.Value = $_.Value;
    return $_;
} | Format-Table -HideTableHeaders

Write-Host("<<<hyperv_host_io_remote>>>")

$resultlist = @()

foreach ( $volume in $remotecounts) {
    foreach ( $element in $customobjects) {
        $checkString = $volume.Number
        if ($element.Path -match "\($checkString\)") {
            $element.Path = [regex]::Replace($element.Path, '\\\\.*\\physicaldisk\(.*\)\\',$idtolun[$checkString]+'\')
            $resultlist += $element
        }
    }
}

$resultlist | Format-Table -HideTableHeaders

Write-Host -NoNewLine "<<<hyperv_dynamicvhdx:sep(59)>>>"
Write-Host ""
# Auslesen aller dynamischen Dateien
$VMs = Get-SCVirtualMachine 

foreach ($VM in $VMs)
{
    $Disks = Get-VM $VM | Get-SCVirtualHardDisk
	foreach ($Disk in $Disks)
	{
		if ($Disk.VHDType -ne "FixedSize")
		{
			$DiskLocation = $Disk.Location
			$CSVVolume = ($Disk.Location.Split("\"))[2]
			$DiskName = ($Disk.Location.Split("\"))[-1]
			$Value = $VM.Name + ";" + $DiskName + ";" + $CSVVolume + ";"
            write-host $Value
		}
	}
}
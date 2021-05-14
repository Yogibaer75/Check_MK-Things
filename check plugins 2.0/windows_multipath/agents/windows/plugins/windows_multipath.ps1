###

$pswindow = $host.ui.rawui
$newsize = $pswindow.buffersize
$newsize.height = 300
$newsize.width = 200
$pswindow.Set_BufferSize($newsize)

###

$result = Get-CimClass -Namespace root/WMI | Where-Object CimClassName -Like "mpio_disk_info"
if ($null -ne $result) {
    Write-Host('<<<windows_multipath:sep(124)>>>')
    (Get-CimInstance -Namespace root/WMI -ClassName mpio_disk_info).driveinfo | ForEach-Object { Write-Host "$($_.name)|$($_.numberpaths)" }    
}

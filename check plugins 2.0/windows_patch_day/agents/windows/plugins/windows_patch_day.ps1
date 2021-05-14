###

$pswindow = $host.ui.rawui
$newsize = $pswindow.buffersize
$newsize.height = 300
$newsize.width = 200
$pswindow.Set_BufferSize($newsize)

###

Write-Host("<<<windows_patch_day:sep(124)>>>")
Get-CimInstance -ClassName win32_reliabilityRecords `
| Where-Object {$_.sourcename -eq "Microsoft-Windows-WindowsUpdateClient"} `
| Sort-Object timegenerated -desc `
| ForEach-Object {write-host($_.productname + "|" + $_.timegenerated)}

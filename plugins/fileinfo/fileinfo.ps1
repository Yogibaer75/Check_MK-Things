Write-Output "<<<fileinfo:sep(124)>>>"
$date1 = Get-Date -Date "01/01/1970"
$date_now = [int]([DateTime]::UtcNow - $date1).TotalSeconds
Write-Output $date_now
$files =  Get-ChildItem C:\Temp -rec | Where-Object {! $_.PSIsContainer} 
foreach($object in $files)
{
    $time_1 = ($object.LastWriteTime).ToFileTime()
    $timestamp = [int]([datetime]::fromfiletime($time_1) - $date1).TotalSeconds
    Write-Host ($object.FullName,$object.length,$timestamp) -Separator "|"
}
$dirs = Get-ChildItem C:\Temp -rec | Where-Object {$_.PSIsContainer -eq $True} | Where-Object {$_.GetFiles().Count -eq 0}
foreach($object in $dirs)
{
    $missing_dir = $object.FullName + "\*.*"
    Write-Host ($missing_dir,"missing",$date_now) -Separator "|"
}

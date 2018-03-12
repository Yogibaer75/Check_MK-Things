Write-Output "<<<fileinfo:sep(124)>>>"
$date1 = Get-Date -Date "01/01/1970"
$filepath = "C:\Temp"
$date_now = [int]([DateTime]::UtcNow - $date1).TotalSeconds
Write-Output $date_now
$dirs = Get-ChildItem $filepath -rec | Where-Object {$_.PSIsContainer -eq $True}
foreach($object in $dirs)
{
    if ($object.GetFiles().Count -eq 0) {
        $missing_dir = $object.FullName + "\*.*"
        Write-Host ($missing_dir,"missing",$date_now) -Separator "|"
    }
    else {
        $files =  Get-ChildItem $object.FullName | Where-Object {! $_.PSIsContainer} 
        foreach($object in $files)
        {
            $time_1 = ($object.LastWriteTime).ToFileTime()
            $timestamp = [int]([datetime]::fromfiletimeutc($time_1) - $date1).TotalSeconds
            Write-Host ($object.FullName,$object.length,$timestamp) -Separator "|"
        }
    }
}

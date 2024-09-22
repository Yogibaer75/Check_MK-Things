Write-Host "<<<windows_dedup:sep(58)>>>"
$VolumeList = Get-DedupVolume

Foreach ($Vol in $VolumeList)
{
    $Vol | Format-List -Property Volume,Enabled,Capacity,FreeSpace,UsedSpace,UnoptimizedSize,SavedSpace,SavingsRate
}


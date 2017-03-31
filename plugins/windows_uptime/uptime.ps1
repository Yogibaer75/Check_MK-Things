function Get-Uptime {
    $os = Get-WmiObject win32_operatingsystem
    $uptime = (Get-Date) - ($os.ConvertToDateTime($os.lastbootuptime))
    $seconds = [int]$uptime.TotalSeconds
    $Display = "<<<uptime>>>`r`n$seconds"
    Write-Output $Display
}

get-uptime
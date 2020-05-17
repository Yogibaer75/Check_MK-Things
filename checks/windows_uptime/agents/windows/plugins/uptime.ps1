function Get-Uptime {
    $os = Get-CimInstance win32_operatingsystem
    $timediff = (Get-Date) - ($os.lastbootuptime)
    $seconds = [int]$timediff.TotalSeconds
    $Display = "<<<uptime>>>`r`n$seconds"
    Write-Output $Display
}

get-uptime
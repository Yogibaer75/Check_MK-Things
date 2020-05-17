Write-Host "<<<tcp_conn_stats>>>"
$stateList = "LISTEN", "TIME_WAIT", "ESTABLISHED", "FIN_WAIT2", "CLOSE_WAIT"
$c = netstat -aonp TCP | ForEach-Object {
    $_ -replace "ABH", "LISTEN" `
        -replace "WARTEND", "TIME_WAIT" `
        -replace "HERGESTELLT", "ESTABLISHED" `
        -replace "FIN_WARTEN_2", "FIN_WAIT2" `
        -replace "SCHLIESSEN_WARTEN", "CLOSE_WAIT"
}
foreach ($s in $stateList) {
    $anzahl = 0
    foreach ($line in $c) {   
        $count = ([regex]::Matches($line, $s )).count
        $anzahl = $anzahl + $count
    }
    Write-Host $s $anzahl
}

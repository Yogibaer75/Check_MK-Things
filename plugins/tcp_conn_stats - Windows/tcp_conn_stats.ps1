Write-Host "<<<tcp_conn_stats>>>"
$stateList = "LISTEN", "TIME_WAIT", "ESTABLISHED", "FIN_WAIT2", "CLOSE_WAIT"
$c = netstat -aonp TCP | % {$_.replace("ABH","LISTEN")} | % {$_.replace("WARTEND","TIME_WAIT")} | % {$_.replace("HERGESTELLT","ESTABLISHED")} | % {$_.replace("FIN_WARTEN_2","FIN_WAIT2")} | % {$_.replace("SCHLIESSEN_WARTEN","CLOSE_WAIT")}
foreach($s in $stateList)
{
    $anzahl = 0
    foreach($line in $c)
    {   
        $count = ([regex]::Matches($line, $s )).count
        $anzahl = $anzahl + $count
    }
    Write-Host $s $anzahl
}

###

$pswindow = $host.ui.rawui
$newsize = $pswindow.buffersize
$newsize.height = 300
$newsize.width = 200
$pswindow.Set_BufferSize($newsize)

###

Write-Host("<<<win_firewall_status:sep(124)>>>")
Write-Host("Profile|Enabled|Inbound|Outbound")
Get-NetFirewallProfile -PolicyStore activestore `
| ForEach-Object { '{0}|{1}|{2}|{3}' -f $_.name, $_.enabled, $_.DefaultInboundAction, $_.DefaultOutboundAction }

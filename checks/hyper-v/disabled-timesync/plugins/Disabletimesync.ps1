Write-Host -NoNewLine "<<<hyperv_disabletimesync>>>"

$Server = hostname
get-VMIntegrationService -name 'Zeitsynchronisierung' -Computername $Server -Vmname * | format-table -HideTableHeaders
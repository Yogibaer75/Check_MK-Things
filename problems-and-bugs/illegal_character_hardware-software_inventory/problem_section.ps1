# System
write-host "<<<win_system:sep(58):persist($until)>>>"
$system = Get-WmiObject Win32_SystemEnclosure -ComputerName $name
$system_vars = @( "Manufacturer","Name","Model","HotSwappable","InstallDate","PartNumber","SerialNumber" )
foreach ( $entry in $system ) { foreach ( $item in $system_vars) {  write-host $item ":" $entry.$item } }

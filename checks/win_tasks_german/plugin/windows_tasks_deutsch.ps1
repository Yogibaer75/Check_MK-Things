Write-Output '<<<windows_tasks:sep(58)>>>'
schtasks /query /fo csv -v `
| ConvertFrom-Csv `
| Where-Object { $_.HostName -match "^$($Env:Computername)$" -and $_.Aufgabenname -notlike '\Microsoft*' } `
| Format-List @{Name = 'TaskName'; Expression = { $_.Aufgabenname } }, @{Name = 'Last Run Time'; Expression = { $_.'Letzte Laufzeit' } }, @{Name = 'Next Run Time'; Expression = { $_.'N�chste Laufzeit' } }, @{Name = 'Last Result'; Expression = { $_.'Letztes Ergebnis' } }, @{Name = 'Scheduled Task State'; Expression = { $_.'Status der geplanten Aufgabe' } }
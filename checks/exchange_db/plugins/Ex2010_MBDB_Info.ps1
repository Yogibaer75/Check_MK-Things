Add-PSSnapin Microsoft.Exchange.Management.PowerShell.E2010
Write-Host '<<<Ex2010_MBDB_Info>>>'
Get-MailboxDatabase -Status -Server (hostname) | ForEach-Object { 
    '{0,-10} {1,-20} {2, -6}' -f ($_.name -replace ' ', '_'), ($_.Databasesize -replace ',', '' -replace '^.*\((.*) bytes\)', '$1'), (Get-MailboxStatistics -Database $_.name).count 
}

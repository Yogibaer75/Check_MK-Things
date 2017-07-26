if ( (Get-PSSnapin -Name Microsoft.Exchange.Management.PowerShell.E2010 -ErrorAction:SilentlyContinue) -eq $null)
{
  Add-PSSnapin Microsoft.Exchange.Management.PowerShell.E2010
}

$mailitems = Get-MailboxFolderStatistics -Identity bla@bla.com -IncludeOldestAndNewestItems -FolderScope Inbox | Where-Object {$_.name -eq "Posteingang"}
$mailage = $mailitems.OldestItemReceivedDate
$date = (get-date).ToString('G')

$compare = new-timespan -start $mailage -end $date
$minutes = $compare.TotalMinutes

echo "P Mailage age=$minutes,60,120 The Age of the oldest Mail is $minutes"

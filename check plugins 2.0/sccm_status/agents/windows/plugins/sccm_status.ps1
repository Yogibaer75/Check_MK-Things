###

$pswindow = $host.ui.rawui
$newsize = $pswindow.buffersize
$newsize.height = 300
$newsize.width = 200
$pswindow.Set_BufferSize($newsize)

###

$SiteCode = (Get-CimInstance -Namespace "root\sms" -class "__Namespace").Name.Substring(5,3)
$SiteHost = (Get-CimInstance win32_computersystem).DNSHostName+"."+(Get-CimInstance win32_computersystem).Domain

Write-Host "<<<sccm_status:sep(9)>>>"
Get-CimInstance -Namespace root\sms\Site_$SiteCode -query "Select * from SMS_SiteSystemSummarizer" -ComputerName $SiteHost `
| Select-Object status,role,sitecode,percentfree,objecttype,sitesystem `
| ConvertTo-Csv -Delimiter "`t" -NoTypeInformation

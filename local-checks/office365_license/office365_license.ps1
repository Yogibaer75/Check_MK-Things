Import-Module MSOnline

$AdminName = "admin@mydomain.com"
$Pass = Get-Content "C:\temp\cred.txt" | ConvertTo-SecureString
$cred = new-object -typename System.Management.Automation.PSCredential -argumentlist $AdminName, $Pass

Connect-MsolService -Credential $cred

$licenses_all = Get-MsolAccountSku | Where-Object {$_.AccountSkuId -eq "xxxxxx"} | ForEach-Object {$_.ActiveUnits}
$licenses_used = Get-MsolAccountSku | Where-Object {$_.AccountSkuId -eq "xxxxx"} | ForEach-Object {$_.ConsumedUnits}
$licenses_free = $licenses_all - $licenses_used

Write-Output "P Office365_LicensingStatus licenses=$licenses_free;5:999;0:999;; Free licenses left"
###

$pshost = Get-Host              # Get the PowerShell Host.
$pswindow = $pshost.UI.RawUI    # Get the PowerShell Host's UI.

$newsize = $pswindow.BufferSize # Get the UI's current Buffer Size.
$newsize.height = 300          # Set the new buffer's heigt to 300 lines.
$newsize.width = 200            # Set the new buffer's width to 200 columns.
$pswindow.buffersize = $newsize # Set the new Buffer Size as active.

$newsize = $pswindow.windowsize # Get the UI's current Window Size.
$newsize.width = 200            # Set the new Window Width to 200 columns.
$pswindow.windowsize = $newsize # Set the new Window Size as active.

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($true)

###

# config file directory
$MK_CONFDIR = $env:MK_CONFDIR

# Fallback if no MK_CONFDIR is set
if (!$MK_CONFDIR) {
    $MK_CONFDIR= "$env:ProgramData\checkmk\agent\config"
}

# Read the config file - attention this is no source of the file as it needs to be read in UTF-8
$CONFIG_FILE="${MK_CONFDIR}\windows_patch_day.cfg"
if (test-path -path "${CONFIG_FILE}" ) {
    $values = Get-Content -Path "${CONFIG_FILE}" -Encoding UTF8 | Out-String | ConvertFrom-StringData
    $filterstring = $values.filterstring.split("|")
    $updatecount = $values.updatecount
}

# If no config file is loaded use the default settings
if (!$updatecount) {
    $updatecount = 30
}

if (!$filterstring) {
    $filterstring = '#######'
}
[regex] $filter_regex ='(?i)^(' + (($filterstring |ForEach-Object {[regex]::escape($_)}) -join "|") + ')'

Write-Host('<<<windows_patch_day:sep(124)>>>')
$Searcher = (New-Object -ComObject Microsoft.Update.Session).CreateUpdateSearcher()
$HistoryCount = $Searcher.GetTotalHistoryCount()
if ($HistoryCount -eq 0) {
    exit 0
}
$Searcher.QueryHistory(0, $HistoryCount) `
| Where-Object { $_.title -notmatch $filter_regex -AND $_.title -ne $null } `
| Sort-Object date -desc `
| Select-Object -First $updatecount `
| ForEach-Object { Write-Host($_.title + '|' + $_.date + '|' + $_.resultcode) }

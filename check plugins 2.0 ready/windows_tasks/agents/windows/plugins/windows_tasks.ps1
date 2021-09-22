###

$pshost = Get-Host              # Get the PowerShell Host.
$pswindow = $pshost.UI.RawUI    # Get the PowerShell Host's UI.

$newsize = $pswindow.BufferSize # Get the UI's current Buffer Size.
$newsize.height = 300          # Set the new buffer's heigt to 300 lines.
$newsize.width = 200            # Set the new buffer's width to 200 columns.
$pswindow.buffersize = $newsize # Set the new Buffer Size as active.

$newsize = $pswindow.windowsize # Get the UI's current Window Size.
$newsize.width = 200            # Set the new Window Width to 1200 columns.
$pswindow.windowsize = $newsize # Set the new Window Size as active.

###

Write-Host '<<<windows_tasks:sep(124)>>>'
Write-Host 'TaskName|LastRunTime|NextRunTime|LastTaskResult|State|NumberOfMissedRuns'
$tasks = Get-ScheduledTask
$tasks | Where-Object { $_.TaskPath -notlike '\Microsoft\*' } | Get-ScheduledTaskInfo | ForEach-Object {
    $task = $tasks | Where-Object TaskName -eq $_.TaskName
    '{0}|{1}|{2}|{3}|{4}|{5}' -f $_.TaskName, $_.LastRunTime, $_.NextRunTime, $_.LastTaskResult, $task.state, $_.NumberOfMissedRuns
}

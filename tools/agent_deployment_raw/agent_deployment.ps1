$computers = Get-Content -path hostlist.txt

foreach ($i in $computers){
  Write-Host $i 
  $DestPath = "\\"+"$i"+"\c$\temp\"
  if (!( Test-Path $DestPath ))
   {
     New-Item $DestPath -ItemType Dir
   }
  $Arg = "C:\Temp\PsExec.exe \\"+"$i"+" C:\temp\install_agent-universal.exe /S"
  Copy-Item -Path C:\Temp\install_agent-universal.exe -Destination $DestPath -Recurse -Force
  Invoke-Command -ScriptBlock { & cmd /c $Arg }
}

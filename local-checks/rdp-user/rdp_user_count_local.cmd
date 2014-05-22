@ECHO OFF
SET /a COUNTA=0
SET /a COUNTD=-1

FOR /f "TOKENS=1 DELIMS= " %%G IN ('query session ^|find "rdp-tcp#"') DO SET /a COUNTA+=1
FOR /f "TOKENS=1 DELIMS= " %%G IN ('query session ^|find "Getr"') DO SET /a COUNTD+=1

ECHO 0 RDP-User-Count usersconnected=%COUNTA%;1;2^|usersdisconnected=%COUNTD%;1;2 Active sessions = %COUNTA%, Disconnected Sessions = %COUNTD%

strComputer = "."

Set objWMIService = GetObject("winmgmts:\\" & strComputer & "\root\cimv2") 
Set colDevices = objWMIService.ExecQuery ("Select * From Win32_USBControllerDevice") 
Wscript.echo("<<<local>>>")
For Each objDevice in colDevices 
    strDeviceName = objDevice.Dependent 
    strQuotes = Chr(34) 
    strDeviceName = Replace(strDeviceName, strQuotes, "") 
    arrDeviceNames = Split(strDeviceName, "=") 
    strDeviceName = arrDeviceNames(1) 
    Set colUSBDevices = objWMIService.ExecQuery ("Select * From Win32_PnPEntity Where DeviceID = '" & strDeviceName & "'") 
    For Each entry in colUSBDevices 
        For Each item in entry.Properties_
            arrVars = Array ( "Description" )
            If UBound(filter(arrVars, item.name)) = 0 Then
                clean_string = Replace(item.value, "(","")
                clean_string = Replace(clean_string, ")","")
                clean_string = Replace(clean_string, "ä","ae")
                clean_string = Replace(clean_string, "ö","oe")
                clean_string = Replace(clean_string, "ü","ue")
                clean_string = Replace(clean_string, " ","_")
                clean_string = Replace(clean_string, "+","")
                clean_string = Replace(clean_string, ".","")
                Wscript.echo("0 USB-Device-" & clean_string &" - " & item.value)
            End If
        Next
    Next
Next
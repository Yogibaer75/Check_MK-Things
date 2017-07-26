' -----------------------------------------------------------------------------
' Check_MK windows agent plugin to gather information from local MSSQL servers
'
' This plugin can be used to collect information of all running MSSQL server
' on the local system.
'
' The current implementation of the check uses the "trusted authentication"
' where no user/password needs to be created in the MSSQL server instance by
' default. It is only needed to grant the user as which the Check_MK windows
' agent service is running access to the MSSQL database.
'
' Another option is to create a mssql.ini file in MK_CONFDIR and write the
' credentials of a database user to it which shal be used for monitoring:
'
' [auth]
' type = db
' username = monitoring
' password = secret-pw
'
' The following sources are asked:
' 1. Registry - To gather a list of local MSSQL-Server instances
' 2. WMI - To check for the state of the MSSQL service
' 2. MSSQL-Servers via ADO/sqloledb connection to gather infos these infos:
'      a) list and sizes of available databases
'      b) counters of the database instance
'
' This check has been developed with MSSQL Server 2008 R2. It should work with
' older versions starting from at least MSSQL Server 2005.
' -----------------------------------------------------------------------------

Option Explicit

Dim WMI, FSO, SHO, items, objItem, prop, instVersion, registry
Dim sources, instances, instance, instance_id, instance_name
Dim cfg_dir, cfg_file, hostname

Const HKLM = &H80000002

' Directory of all database instance names
Set instances = CreateObject("Scripting.Dictionary")
Set FSO = CreateObject("Scripting.FileSystemObject")
Set SHO = CreateObject("WScript.Shell")

hostname = SHO.ExpandEnvironmentStrings("%COMPUTERNAME%")
cfg_dir = SHO.ExpandEnvironmentStrings("%MK_CONFDIR%")

Sub addOutput(text)
    wscript.echo text
End Sub

Function readIniFile(path)
    Dim parsed : Set parsed = CreateObject("Scripting.Dictionary")
    If path <> "" Then
        Dim FH
        Set FH = FSO.OpenTextFile(path)
        Dim line, sec, pair
        Do Until FH.AtEndOfStream
            line = Trim(FH.ReadLine())
            If Left(line, 1) = "[" Then
                sec = Mid(line, 2, Len(line) - 2)
                Set parsed(sec) = CreateObject("Scripting.Dictionary")
            Else
                If line <> "" Then
                    pair = Split(line, "=")
                    If 1 = UBound(pair) Then
                        parsed(sec)(Trim(pair(0))) = Trim(pair(1))
                    End If
                End If
            End If
            Set FH = Nothing
        Loop
        FH.Close
    End If
    Set readIniFile = parsed
    Set parsed = Nothing
End Function

Set registry = GetObject("winmgmts:{impersonationLevel=impersonate}!\\.\root\default:StdRegProv")
Set sources = CreateObject("Scripting.Dictionary")

Dim service, i, version, edition, value_types, value_names, value_raw, cluster_name
Set WMI = GetObject("winmgmts:{impersonationLevel=impersonate}!\\.\root\cimv2")

'
' Gather instances on this host, store instance in instances and output version section for it
'
registry.EnumValues HKLM, "SOFTWARE\Microsoft\Microsoft SQL Server\Instance Names\SQL", _
                          value_names, value_types

If Not IsArray(value_names) Then
    addOutput("ERROR: Failed to gather SQL server instances")
    wscript.quit(1)
End If

' Make sure that always all sections are present, even in case of an error. 
' Note: the section <<<mssql_instance>>> section shows the general state 
' of a database instance. If that section fails for an instance then all 
' other sections do not contain valid data anyway.
'
' Don't move this to another place. We need the steps above to decide whether or
' not this is a MSSQL server.
Dim sections, section_id
Set sections = CreateObject("Scripting.Dictionary")
sections.add "jobs", "<<<mssql_jobs>>>"

For Each section_id In sections.Keys
    addOutput(sections(section_id))
Next

For i = LBound(value_names) To UBound(value_names)
    instance_id = value_names(i)

    registry.GetStringValue HKLM, "SOFTWARE\Microsoft\Microsoft SQL Server\" & _
                                  "Instance Names\SQL", _
                                  instance_id, instance_name

    ' HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Microsoft SQL Server\MSSQL10_50.MSSQLSERVER\MSSQLServer\CurrentVersion
    registry.GetStringValue HKLM, "SOFTWARE\Microsoft\Microsoft SQL Server\" & _
                                  instance_name & "\MSSQLServer\CurrentVersion", _
                                  "CurrentVersion", version

    ' HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Microsoft SQL Server\MSSQL10_50.MSSQLSERVER\Setup
    registry.GetStringValue HKLM, "SOFTWARE\Microsoft\Microsoft SQL Server\" & _
                                  instance_name & "\Setup", _
                                  "Edition", edition

    ' Check whether or not this instance is clustered
    registry.GetStringValue HKLM, "SOFTWARE\Microsoft\Microsoft SQL Server\" & _
                                  instance_name & "\Cluster", "ClusterName", cluster_name

    If IsNull(cluster_name) Then
        cluster_name = ""

        ' In case of instance name "MSSQLSERVER" always use (local) as connect string
        If instance_id = "MSSQLSERVER" Then
            sources.add instance_id, "(local)"
        Else
            sources.add instance_id, hostname & "\" & instance_id
        End If
    Else
        ' In case the instance name is "MSSQLSERVER" always use the virtual server name
        If instance_id = "MSSQLSERVER" Then
            sources.add instance_id, cluster_name
        Else
            sources.add instance_id, cluster_name & "\" & instance_id
        End If
    End If

    ' Only collect results for instances which services are currently running
    Set service = WMI.ExecQuery("SELECT State FROM Win32_Service " & _
                          "WHERE Name = 'MSSQL$" & instance_id & "' AND State = 'Running'")
    If Not IsNull(service) Then
        instances.add instance_id, ""
    End If
Next

Set service  = Nothing
Set WMI      = Nothing
Set registry = Nothing

Dim CONN, RS, CFG, AUTH

' Initialize database connection objects
Set CONN      = CreateObject("ADODB.Connection")
Set RS        = CreateObject("ADODB.Recordset")
CONN.Provider = "sqloledb"
' It's a local connection. 2 seconds should be enough!
CONN.ConnectionTimeout = 2

' Loop all found server instances and connect to them
' In my tests only the connect using the "named instance" string worked
For Each instance_id In instances.Keys: Do ' Continue trick

    ' Use either an instance specific config file named mssql_<instance-id>.ini
    ' or the default mysql.ini file.
    cfg_file = cfg_dir & "\mssql_jobs_" & instance & ".ini"
    If Not FSO.FileExists(cfg_file) Then
        cfg_file = cfg_dir & "\mssql_jobs.ini"
        If Not FSO.FileExists(cfg_file) Then
            cfg_file = ""
        End If
    End If

    Set CFG = readIniFile(cfg_file)
    If Not CFG.Exists("auth") Then
        Set AUTH = CreateObject("Scripting.Dictionary")
    Else
        Set AUTH = CFG("auth")
    End If

    ' At this place one could implement to use other authentication mechanism
    If Not AUTH.Exists("type") or AUTH("type") = "system" Then
        CONN.Properties("Integrated Security").Value = "SSPI"
    Else
        CONN.Properties("User ID").Value = AUTH("username")
        CONN.Properties("Password").Value = AUTH("password")
    End If

    CONN.Properties("Data Source").Value = sources(instance_id)

    ' Try to connect to the instance and catch the error when not able to connect
    ' Then add the instance to the agent output and skip over to the next instance
    ' in case the connection could not be established.
    On Error Resume Next
    CONN.Open
    On Error GoTo 0

    ' Collect eventual error messages of errors occured during connecting. Hopefully
    ' there is only on error in the list of errors.
    Dim error_msg
    If CONN.Errors.Count > 0 Then
        error_msg = CONN.Errors(0).Description
    End If
    Err.Clear

    ' adStateClosed = 0
    If CONN.State = 0 Then
        Exit Do
    End If
    
    addOutput(sections("jobs"))
        RS.Open "SELECT name, sjh.run_status, sjh.run_date, sjh.run_time" &_
                " FROM msdb.dbo.sysjobs sj" &_
                " INNER JOIN msdb.dbo.sysjobhistory sjh ON sj.job_id = sjh.job_id" &_
                " INNER JOIN msdb.dbo.sysjobsteps s ON sjh.job_id = s.job_id" &_
                " AND sjh.step_id = s.step_id" &_
                " WHERE CONVERT(VARCHAR(8), sjh.run_date) > GETDATE() - 1" &_
                " AND sjh.run_status = 0", CONN
        Do While Not RS.Eof
            addOutput( instance_id & " " & Replace(RS("name"), " ", "_") &" " & Replace(RS("run_status"), " ", "_") & " " & Replace(RS("run_date"), " ", "_") & " " & Replace(RS("run_time"), " ", "_"))
            RS.MoveNext
        Loop
        RS.Close
    CONN.Close

Loop While False: Next

Set sources = nothing
Set instances = nothing
Set sections = nothing
Set RS = nothing
Set CONN = nothing
Set FSO = nothing
Set SHO = nothing

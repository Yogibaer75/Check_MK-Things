# config file directory
$MK_CONFDIR = $env:MK_CONFDIR

# Fallback if no MK_CONFDIR is set
if (!$MK_CONFDIR) {
    $MK_CONFDIR= "$env:ProgramData\checkmk\agent\config"
}

# Read the config file - attention this is no source of the file as it needs to be read in UTF-8
$CONFIG_FILE="${MK_CONFDIR}\netbackup.cfg"
if (test-path -path "${CONFIG_FILE}" ) {
    $values = Get-Content -Path "${CONFIG_FILE}" -Encoding UTF8 | Out-String | ConvertFrom-StringData
    $bperror_path = $values.errorpath
} else {
    exit 0
}

write-Output "<<<netbackup_jobs>>>"
# Definiert den Pfad zur ausführbaren Datei
$command = "${bperror_path}bperror.exe"
# Definiert die Argumente für den Befehl
$arguments = @(
    "-backstat",
    "-hoursago",
    "24",
    "-U"
)
# Führt den Befehl mit den Argumenten aus
& $command $arguments

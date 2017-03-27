# Checks und Anpassungen der CMK Checks

## Anpassungen der CMK Komponenten

[check_mkevents.cc mit Option fuer Socket Path versehen](./classic-checks/check_mkevents/)

```cc
char *socket_path         = NULL;

int argc_count = argc;
for (int i = 1; i < argc ; i++) {
    if (!strcmp("-H", argv[i]) && i < argc + 1) {
        remote_host = argv[i+1];
        i++;
        argc_count -= 2;
    }
    else if (!strcmp("-S", argv[i]) && i < argc + 1) {
        socket_path = argv[i+1];
        i++;
        argc_count -= 2;
    } 

if (omd_path)
    snprintf(unixsocket_path, sizeof(unixsocket_path), "%s/tmp/run/mkeventd/status", omd_path);
else if (socket_path)
    snprintf(unixsocket_path, sizeof(unixsocket_path), "%s", socket_path );
else {
    printf("UNKNOWN - OMD_ROOT is not set, no socket path is defined.\n");
    exit(3);
}
```
Extra noch wurden die Icons und die Generierung der aktiven MKEvent Checks angepasst.

[Win Printers geaendert das Offline Network Printer nicht critical werden](./checks/win_printers/)

[Sidebar Snapin mit allen Services welche Notification an haben](./erweiterungen-webseite/sidebar_snapin_service_problem_short/)

[check_bi_local.py angepasst das JSON Output erzeugt wird](./local-checks/local_check_bi/)

[Dashboard nur mit Host mit aktivierter Benachrichtigung](./erweiterungen-webseite/dashboard_mit_benachrichtigung_only/)

Weitere Anpassungen

## Eigene Checks

[Etherbox Check um Spannungscheck und "no connected Sensor" erweitert](./checks/etherbox/)

[APC PDU Check fuer die Leistung der Anschluesse](./checks/apc_pdu/)

## Eigene Agent Scripte

[Remote IPMI Agent Script](./datasource-programms/agent_ipmi/)

## Piggyback Example

[Website Scrapping und Piggyback Check](./plugins/plugin_piggybag_example_webscrapping/)

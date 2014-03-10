# Cisco WLC Checks

Checks so angepasst damit auch andere WLC gefunden werden.
´´´
    "snmp_scan_function"    : lambda oid: oid('.1.3.6.1.2.1.1.2.0') in [".1.3.6.1.4.1.9.1.1069", ".1.3.6.1.4.1.9.1.1279"],
´´´
Hier können auch einfach weitere OID's hinzugefügt werden.
Unter der OID ".1.3.6.1.2.1.1.2.0" kann an jedem Gerät geschaut werden mit welcher OID es sich meldet.

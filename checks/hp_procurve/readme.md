# HP Procurve Checks

Checks so angepasst damit auch andere Typen von Procurve gefunden werden.
´´´
    'snmp_scan_function':      \
     lambda oid: oid(".1.3.6.1.2.1.1.2.0") in [
                               ".1.3.6.1.4.1.11.2.3.7.11",
                               ".1.3.6.1.4.1.11.2.3.7.8.5.3",
                           ],
´´´
Hier können auch einfach weitere OID's hinzugefügt werden.
Unter der OID ".1.3.6.1.2.1.1.2.0" kann an jedem Gerät geschaut werden mit welcher OID es sich meldet.

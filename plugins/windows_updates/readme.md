# Patch fuer Windows Updates Check

Der Patch verhindert das eine 0 Byte große Cache Datei fuer laengere Zeit erhalten bleibt
und nicht durch die korrekte Cache Datei ersetzt werden kann.

erstellt von Thomas Tretbar

Der Patch ist seit dem neuen Caching Mechanismus in 1.2.4 nicht mehr notwendig da dort der Cache selber im RAM gehalten wird.
Refresh des Cache ist über normalen restart des Service möglich.

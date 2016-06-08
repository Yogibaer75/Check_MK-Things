#BUG Beschreibung

Bei Verwendung vom Agent 1.2.8 oder neuer wird der Output ja immer als Unicode übertragen.
Damit schlägt der Check fehl da er die Strings nicht mehr richtig findet.
Wird nun im Check der String als Unicode angegeben funktioniert alles wieder.
Getestet hab ich das auch mit einem älteren Agenten und keine Fehler erhalten.
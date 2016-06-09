#BUG Beschreibung

auf einem Cisco WLC koennen WLANs mit gleichem Namen mehrmals vorhanden sein. Der Check findet diese dann nur einmal und stellt auch 
die verbundenen Clients dann nicht richtig dar. Fuer eine korrekte Darstellung ist es notwendig die ID noch aus zu lesen und dem Namen
als Praefix oder Suffix hinzu zu fuegen.

Es ist notwendig die Geraete neu zu inventarisieren nach der Aenderung.
# BUG Beschreibung
hp_proliant_raid erkennt im vorliegenden Fall nur immer das erste Raid da die Raids normal keine Bezeichnung aufweisen.
Der Check wurde so erweitert, dass die Array Number noch mit eingelesen wird und bei fehlender Bezeichnung das Item bildet.
Ebenfalls wurde der Check so gestaltet das Arrays mit Bezeichnung weiterhin normal gecheckt und auch gleich inventarisiert werden.

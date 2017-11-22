# Gitea als Webfronend im Check_MK mit aktiviertem Git

Download Gitea
`wget https://dl.gitea.io/gitea/1.3/gitea-1.3-linux-amd64`

Datei nach `/omd/sites/<sitename>/local/bin` verschieben
in "gitea" umbenennen und ausführbar machen mittels
`chmod +x gitea`
erster Start erfolgt mittels
`gitea web` Achtung unter dem Site User starten
danach ist unter `http://<IP>:3000/` gitea erreichbar
hier die ersten Einstellungen anpassen je nach Wunsch
noch einen Benutzer anlegen mittels

`./gitea admin create-user --name cmkadmin --password cmkadmin --email cmkadmin@example.com`

nun login in der Weboberfläche mittels diesem Benutzer
ein Repo erzeugen

Innerhalb von WATO einmal den Schalter
`Use GIT version control for WATO` aktivieren
und einmal eine Änderung tätigen und danach die "Changes" aktivieren

Nun auf der Shell ins Verzeichnis `~/etc/check_mk` wechseln
mittels `ls -lisa` Kontrolle ob ein Verzeichnis `.git` existiert
`git status` darf keine Fehler bringen

nun die Verknüpfung mit dem remote Repo im Gitea
`git remote add origin http://cmkadmin:cmkadmin@localhost:3000/cmkadmin/check_mk.git`
`git push -u origin master`
danach sind alle Änderungen welche bisher gemacht wurden im Gitea in der Weboberfläche sichtbar
Ab jetzt wird jede einzelne Änderung im GIT protokoliert

Fehlt nur noch der automatische Abgleich zwischen dem lokalen Verzeichnis `etc/check_mk` und
dem remote Repo

Dafür ins Verzeichnis `~/etc/check_mk/.git/hooks` wechseln
Hier die Datei "post-commit" anlegen

```bash
#!/bin/sh
git push -u origin master
```

mittels `chmod +x post-commit` noch ausführbar machen fertig

Nun wird jede Änderung auch automatisch an das Gitea gepushed.

Sollte ein externes GIT Repo schon vorhanden sein kann dies natürlich auch anstatt Gitea benutzt werden.

Hier noch wie man Gitea in OMD integriert für automatischen Start usw.

Init Script nach `~/etc/init.d` in der Site kopieren und ausführbar machen
Im Verzeichnis `/omd/sites/<site>/lib/omd/hooks` eine Datei "GITEA" anlegen wie im Beispiel und diese auch ausführbar machen
Achtung geht nur als `<Root>` da die Datei im allgemeinen OMD Verzeichnis liegt
`omd config` aufrufen und kontrollieren ob die Option da ist

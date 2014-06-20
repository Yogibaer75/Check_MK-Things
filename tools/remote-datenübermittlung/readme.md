# Remote Datenübermittlung zu zentralem Monitoring System

## Übermittlung per SSH

## Übermittlung per Mail

### Sendeseite

Auf der Senderseite werden hauptsächlich zwei Scripts ausgeführt um einmal Daten
und einmal Konfigurationen zu übermitteln. Beide Scripte werden per Cronjob ausgeführt.

Livestatus Data Dump
```bash
#!/bin/bash
cd ~/tmp/
rm data_live
~/local/bin/livedump > ~/tmp/data_live
echo <geheim> | gpg --batch -q --passphrase-fd 0 --cipher-algo AES256 -c ~/tmp/data_live
mv ~/tmp/data_live.gpg ~/tmp/data_live.zip
echo "data mail" | mutt -a ~/tmp/data_live.zip -s "data mail" nagios@bech-noc.de
```

Livestatus Config Dump
```bash
#!/bin/bash

cd ~/tmp/
rm config_live
~/local/bin/livedump -C > ~/tmp/config_live
echo <geheim> | gpg --batch -q --passphrase-fd 0 --cipher-algo AES256 -c ~/tmp/config_live
mv ~/tmp/config_live.gpg ~/tmp/config_live.zip
echo "config mail" | mutt -a ~/tmp/config_live.zip -s "config mail" nagios@bech-noc.de
```

Bestandteil der Scripte ist hautpsächlich dei Abfrage des Livestatus und danach das
Einpacken der erhaltenen Daten in eine E-Mail. Der Versand erfolgt danach auch automatisch.
Nachteil ist es wird lokal nicht überwacht ob die Mail auch versendet wurde.

### Empfangsseite

Die Mails werden auf der Empfangsseite vom Mailserver automatisch in einem Maildir
Verzeichnis abgelegt. Maildir wurde gewählt da jede Mail eine eigene Datei bekommt.

Postfix Konfiguration Anpassung
```ini
# DELIVERY TO MAILBOX
#
# The home_mailbox parameter specifies the optional pathname of a
# mailbox file relative to a user's home directory. The default
# mailbox file is /var/spool/mail/user or /var/mail/user.  Specify
# "Maildir/" for qmail-style delivery (the / is required).
#
#home_mailbox = Mailbox
home_mailbox = Maildir/

# (the value on the table right-hand side is not used).
#
mynetworks = 192.168.144.22/32, 127.0.0.0/8, 217.7.17.0/24
#mynetworks = $config_directory/mynetworks
#mynetworks = hash:/etc/postfix/network_table

# 217.7.17.0 - Netzwerk des SVN

smtpd_client_restrictions = permit_mynetworks,REJECT
# nur Mail von mynetworks annehmen
```

Wichtig ist hier die Einschränkung der zum Empfang erlaubten IP. Ausgeführt wird auf
der Empfangsseite regelmässig das foldende Script welches die Nutzdaten aus den Mails heraus
löst und diese dann entschlüsselt.

```bash
!/bin/bash

cd ~
./bin/unpack.py /usr/local/nagios/Maildir/new/* -d /tmp
rm /usr/local/nagios/Maildir/new/*
if [ -f /tmp/data_live.zip ];
then
    echo <geheim> | gpg --batch -q -o /usr/local/nagios/var/spool/checkresults/ca1b2c8 --passphrase-fd 0 --decrypt /tmp/data_live.zip
    touch /usr/local/nagios/var/spool/checkresults/ca1b2c8.ok
    rm /tmp/data_live.zip
fi
if [ -f /tmp/config_live.zip ];
then
    rm /usr/local/nagios/etc/remote/skd.cfg
    echo <geheim> | gpg --batch -q -o /usr/local/nagios/etc/remote/skd.cfg --passphrase-fd 0 --decrypt /tmp/config_live.zip
    rm /tmp/config_live.zip
fi
```
Das Lösen der Anhänge von den Mails wird mittels des aufgerufenen Python Script unpack.py
erledigt. Dieses Script verarbeitet alle Mails innerhalb der angegebenen Maildir.

```python
#!/usr/bin/python

import os
import sys
import email
import errno
import mimetypes

from optparse import OptionParser

def main():
    parser = OptionParser(usage="""Hilfetext""")
    parser.add_option('-d', '--directory',
                      type='string', action='store',
                      help="""Hilfe""")
    opts, args = parser.parse_args()
    if not opts.directory:
        parser.print_help()
        sys.exit(1)

    try:
        msgfile = args[0]
    except IndexError:
        parser.print_help()
        sys.exit(1)

    fp = open(msgfile)
    msg = email.message_from_file(fp)
    fp.close()

    counter = 1
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart' or part.get_content_maintype() == 'text':
            continue
        filename = part.get_filename()
        if not filename:
            continue
        fp = open(os.path.join(opts.directory, filename), 'wb')
        fp.write(part.get_payload(decode=True))
        fp.close()

if __name__ == '__main__':
    main()

```

Das Script kann auf jeden Fall noch optimiert werden - erste Version :)

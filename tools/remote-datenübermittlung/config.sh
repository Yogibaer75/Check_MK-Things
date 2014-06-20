#!/bin/bash

cd ~/tmp/
rm config_live
~/local/bin/livedump -C > ~/tmp/config_live
echo password | gpg --batch -q --passphrase-fd 0 --cipher-algo AES256 -c ~/tmp/config_live
mv ~/tmp/config_live.gpg ~/tmp/config_live.zip
echo "config mail" | mutt -a ~/tmp/config_live.zip -s "config mail" nagios@bech-noc.de


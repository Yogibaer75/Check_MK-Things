#!/bin/bash
cd ~/tmp/
rm data_live
~/local/bin/livedump > ~/tmp/data_live
echo password | gpg --batch -q --passphrase-fd 0 --cipher-algo AES256 -c ~/tmp/data_live
mv ~/tmp/data_live.gpg ~/tmp/data_live.zip
echo "data mail" | mutt -a ~/tmp/data_live.zip -s "data mail" nagios@bech-noc.de


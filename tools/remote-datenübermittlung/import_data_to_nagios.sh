#!/bin/bash

cd ~
./bin/unpack.py /usr/local/nagios/Maildir/new/* -d /tmp
rm /usr/local/nagios/Maildir/new/*
if [ -f /tmp/data_live.zip ];
then
    echo password | gpg --batch -q -o /usr/local/nagios/var/spool/checkresults/ca1b2c8 --passphrase-fd 0 --decrypt /tmp/data_live.zip
    touch /usr/local/nagios/var/spool/checkresults/ca1b2c8.ok
    rm /tmp/data_live.zip
fi
if [ -f /tmp/config_live.zip ];
then
    rm /usr/local/nagios/etc/remote/skd.cfg
    echo password | gpg --batch -q -o /usr/local/nagios/etc/remote/skd.cfg --passphrase-fd 0 --decrypt /tmp/config_live.zip
    rm /tmp/config_live.zip
fi

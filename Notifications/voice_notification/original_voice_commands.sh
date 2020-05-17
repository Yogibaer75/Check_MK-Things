/usr/bin/printf "%b" "Dies ist eine Nachricht vom Nagios der Firma. Der Service $SERVICEDESC$ auf dem Host $HOSTALIAS$ hat den Status  $SERVICESTATE$."  | /usr/local/nagios/contrib/nagios2asterisk/call.pl -n $CONTACTPAGER$ -c 8595 -C "CAPI/ISDN1/$CONTACTPAGER$" -H $HOSTNAME$ -S "$SERVICEDESC$"

/usr/bin/printf "%b" "Dies ist eine Nachricht vom Nagios der Firma. Der Host $HOSTALIAS$ hat den Status  $HOSTSTATE$." | /usr/local/nagios/contrib/nagios2asterisk/call.pl -n $CONTACTPAGER$ -c 8595 -C "CAPI/ISDN1/$CONTACTPAGER$" -H $HOSTNAME$

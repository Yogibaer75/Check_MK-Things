#!/bin/bash
# +------------------------------------------------------------------+

FILES=`find /var/lib/nobody/erfal_ordertransfer/err -maxdepth 1 -type f | wc -l`

echo "P Dateianzahl Files=$FILES;1;2 /var/lib/nobody/test/err"

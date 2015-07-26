#!/bin/bash
# +------------------------------------------------------------------+

USERS=`who --count | wc -l`

echo "P Users users=$USERS;250;260 Benutzer zur Zeit eingeloggt"

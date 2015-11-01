# User Count as local check

This small script counts the users logged in on the system and outputs only
the number.

As alternative you can use the following syntax.

```bash
USERS=`who --count | pcregrep -o 'users=\K.*'`
```
or if `pcregrep` is not available you can use
```bash
USERS=`who | grep -c .`
```

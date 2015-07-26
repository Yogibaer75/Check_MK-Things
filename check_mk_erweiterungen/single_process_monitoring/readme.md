# Single Process monitoring #

For the single process level monitoring you must make some preparations.

* copy `ps` and `ps.include` from `share/check_mk/checks` to `local/share/check_mk/checks`
* the same for `check_parameters.py` from `share/check_mk/web/plugins/wato` to `local/share/check_mk/web/plugins/wato`
* now apply the diff files to the files and restart you webserver inside OMD

Now there should be an option available if you make a rule under `State and count of processes` at the moment it is not possible to set this option already under `Process discovery`

####Example Output Single Process Check

Process Apache       WARN - 26 processes, maximum single process 1259.2 MB virtual(!), 172.3 MB resident, 36.7% CPU

####Example Output normal Check

Process Apache       CRIT - 26 processes 7807.6 MB virtual(!!), 1990.0 MB resident, 8.7% CPU

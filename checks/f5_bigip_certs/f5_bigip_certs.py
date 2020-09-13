#!/usr/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# License: GNU General Public License v2

## Custom check for F5 certificate expiration
## Author: Shaun Pillé
## Contact: shaun.pille@gmail.com
## Version 0.3
## Modification: Andreas Doehler

factory_settings['f5_bigip_certs_default_levels'] = {
    'expire_lower' : (864000, 2592000),
}

def parse_f5_bigip_certs(info):
    parsed = {}
    ignore_list = set (['/Common/default.crt','/Common/f5-irule.crt','/Common/ca-bundle.crt','/Common/f5-ca-bundle.crt'])
    for certname, epochdate in info:
        if certname not in ignore_list:
            parsed[certname] = {"epochdate":epochdate}
    return parsed

#check the expiration dates and return crit, warn, ok based on defined thresholds
@get_parsed_item_data
def check_f5_bigip_certs(item, params, data):
    crit, warn = params.get("expire_lower")
    state = 0
    now = time.time()
    epochdate = int(data.get("epochdate"))
    time_diff = epochdate - currdate

    if epochdate < now:
        infotext = "%s ago" % get_age_human_readable(abs(time_diff))
        state=2
    elif time_diff < crit:
        infotext = "%s to go" % get_age_human_readable(time_diff)
        state=2
    elif time_diff < warn:
        infotext = "%s to go" % get_age_human_readable(time_diff)
        state=1
    else:
        infotext = "%s to go" % get_age_human_readable(time_diff)
        state=0

    if state == 2 and time_diff < 0:
        infotext += " (expire date in the past)"
    elif state > 0:
        infotext += " (warn/crit below %s/%s)" % (get_age_human_readable(warn),
                                                  get_age_human_readable(crit))

    yield state, infotext, [("seconds", time_diff, warn, crit)]

#checkdata to pull matching SNMP strings
check_info["f5_bigip_certs"] = {
    "check_function": check_f5_bigip_certs,
    "inventory_function": discover(),
    "parse_function": parse_f5_bigip_certs,
    "default_levels_variable": "f5_bigip_certs_default_levels",
    "service_description": "Certificate Expiration %s",
    "snmp_info": ( ".1.3.6.1.4.1.3375.2.1.15.1.2.1", [ 1,5 ] )
}
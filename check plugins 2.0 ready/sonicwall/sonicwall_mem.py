#!/usr/bin/env python3
# -*- coding: utf-8 -*-

factory_settings["sonicwall_mem_default_levels"] = {"levels": (80.0, 95.0)}


def inventory_sonicwall_mem(info):
    return [(None, "sonicwall_mem_default_levels")]


def check_sonicwall_mem(_no_item, params, info):
    warn, crit = params.get("levels", (80.0, 95.0))
    data = int(info[0][0])
    perfdata = [("MEMORY", data, warn, crit, 0, 100)]
    if data > crit:
        return (2, "MEMORY is over %s percent" % crit, perfdata)
    elif data > warn:
        return (1, "MEMORY is over %s percent" % warn, perfdata)
    else:
        return (0, "MEMORY is %s percent" % data, perfdata)


check_info["sonicwall_mem"] = {
    "default_levels_variable": "sonicwall_mem_default_levels",
    "check_function": check_sonicwall_mem,
    "inventory_function": inventory_sonicwall_mem,
    "service_description": "Memory",
    "has_perfdata": True,
    "snmp_scan_function": lambda oid: "sonicwall" in oid(".1.3.6.1.2.1.1.1.0").lower(),
    "snmp_info": (".1.3.6.1.4.1.8741.1.3.1.4", [ "0" ]),
}

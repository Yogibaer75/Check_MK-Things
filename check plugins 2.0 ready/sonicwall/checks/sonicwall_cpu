#!/usr/bin/env python3
# -*- coding: utf-8 -*-

factory_settings["sonicwall_cpu_default_levels"] = {"levels": (80.0, 95.0)}


def inventory_sonicwall_cpu(info):
    return [(None, "sonicwall_cpu_default_levels")]


def check_sonicwall_cpu(_no_item, params, info):
    warn, crit = params.get("levels", (80.0, 95.0))
    data = int(info[0][0])
    perfdata = [("CPU", data, warn, crit, 0, 100)]
    if data > crit:
        return (2, "CPU is over %s percent" % crit, perfdata)
    elif data > warn:
        return (1, "CPU is over %s percent" % warn, perfdata)
    else:
        return (0, "CPU is %s percent" % data, perfdata)


check_info["sonicwall_cpu"] = {
    "default_levels_variable": "sonicwall_cpu_default_levels",
    "check_function": check_sonicwall_cpu,
    "inventory_function": inventory_sonicwall_cpu,
    "service_description": "CPU utilization",
    "has_perfdata": True,
    "snmp_scan_function": lambda oid: "sonicwall" in oid(".1.3.6.1.2.1.1.1.0").lower(),
    "snmp_info": (".1.3.6.1.4.1.8741.1.3.1.3", [ "0" ]),
}
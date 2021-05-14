#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.base.check_legacy_includes.temperature import *  # pylint: disable=wildcard-import,unused-wildcard-import
factory_settings["netgear_boxservice_temp_default_levels"] = {"levels": (50.0, 60.0)}


def inventory_netgear_boxservice_temp(info):
    for line in info:
        if savefloat(line[2]) > 0:
            yield (line[0], {})


def check_netgear_boxservice_temp(item, params, info):
    for line in info:
        if line[0] == item:
            return check_temperature(float(line[2]), params, "netgear_boxservice_temp_%s" % item)


check_info["netgear_boxservice_temp"] = {
    "check_function": check_netgear_boxservice_temp,
    "inventory_function": inventory_netgear_boxservice_temp,
    "service_description": "Temperature %s",
    "has_perfdata": True,
    "group": "temperature",
    "snmp_scan_function": lambda oid: oid(".1.3.6.1.2.1.1.2.0").startswith(".1.3.6.1.4.1.4526.100"),
    "snmp_info": (
        ".1.3.6.1.4.1.4526.11.43.1.8.1",
        [
            OID_END,
            "4",  #Sensor Name
            "5",  #Sensor Value
        ]),
    "default_levels_variable": "netgear_boxservice_temp_default_levels"
}

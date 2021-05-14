#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.base.check_legacy_includes.fan import *  # pylint: disable=wildcard-import,unused-wildcard-import


factory_settings["netgear_boxservice_fan_default_levels"] = {
    "upper": (None, None),
    "lower": (2000, 1000),
    "output_metrics": True,
}

def parse_netgear_boxservice_fan(info):
    map_fan_type = {
        "1": "fixed",
        "2": "removable",
        "3": "fixedAC",
        "4": "removableDC",
        "5": "fixedDC",
        "6": "removableAC",
    }
    map_fan_state = {
        "1": (3, "not present"),
        "2": (0, "operational"),
        "3": (2, "failed"),
        "4": (0, "powering"),
        "5": (1, "no power"),
        "6": (1, "not powering"),
        "7": (1, "incompatible"),
    }
    parsed = {}
    for line in info:
        index,fan_type,fan_state,speed = line
        parsed.setdefault(index,{
                 "type": map_fan_type[fan_type],
                 "state": map_fan_state[fan_state],
                 "speed": int(speed)
               })
    return parsed

@get_parsed_item_data
def check_netgear_boxservice_fan(_item, params, entry):

    yield entry["state"][0], 'Status: %s' % entry["state"][1]

    if entry["speed"] in (-99, None):
        return

    yield check_fan(entry["speed"], params)

check_info['netgear_boxservice_fan'] = {
        'inventory_function': discover(),
        'parse_function': parse_netgear_boxservice_fan,
        'check_function': check_netgear_boxservice_fan,
        'service_description': 'Fan %s',
        'group': 'hw_fans',
        'has_perfdata': True,
        'default_levels_variable': "netgear_boxservice_fan_default_levels",
        'snmp_scan_function' : lambda oid: oid('.1.3.6.1.2.1.1.2.0').startswith('.1.3.6.1.4.1.4526.100'),
        'snmp_info': ('.1.3.6.1.4.1.4526.11.43.1.6.1',
         [
                1, # boxServicesFansIndex
                2, # boxServicesFanItemType
                3, # boxServicesFanItemState
                4, # boxServicesFanSpeed
         ]),
}

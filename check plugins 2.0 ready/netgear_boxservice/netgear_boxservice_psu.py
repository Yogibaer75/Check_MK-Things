#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def parse_netgear_boxservice_psu(info):
    map_psu_type = {
        "1": "fixed",
        "2": "removable",
        "3": "fixedAC",
        "4": "removableDC",
        "5": "fixedDC",
        "6": "removableAC",
    }
    map_psu_state = {
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
        psu_nr, type_index, state_index = line
        parsed.setdefault(psu_nr,{
                "type": map_psu_type[type_index],
                "state": map_psu_state[state_index],
            })
    return parsed


@get_parsed_item_data
def check_netgear_boxservice_psu(item, _no_params, data):
    state, state_readable = data["state"]
    return state, "[%s] Operational status: %s" % (data["type"], state_readable)


check_info['netgear_boxservice_psu'] = {
    'parse_function': parse_netgear_boxservice_psu,
    'inventory_function': discover(),
    'check_function': check_netgear_boxservice_psu,
    'service_description': 'Power Supply %s',
    'snmp_info': (".1.3.6.1.4.1.4526.11.43.1.7.1", [OID_END,"2","3"]),
    'snmp_scan_function': lambda oid: oid(".1.3.6.1.2.1.1.2.0").startswith(".1.3.6.1.4.1.4526.100"),
}

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

factory_settings["sonicwall_conns_default_levels"] = {"levels": (80.0, 95.0)}


def parse_sonicwall_conns(info):
    """
    parse info data and create dictionary with namedtuples for each OID.

    {
       oid_end : (con_max, con_current)
    }

    :param info: parsed snmp data
    :return: dictionary
    """
    con_dict = {}
    for oid_end, con_max, con_current in info:
        con_dict[str(oid_end)] = (int(con_max),
                                  int(con_current))
    return con_dict


def inventory_sonicwall_conns(parsed):
    return [(oid_end, {}) for oid_end in parsed]


@get_parsed_item_data
def check_sonicwall_conns(item, params, data):
    warn, crit = params.get("levels", (80, 95))
    con_max, con_current = data
    percent = int(100 * con_current/con_max)
    perfdata = [("CONNECTIONS", percent, warn, crit, 0, 100)]
    if percent > crit:
        return (2, "Too many connections: %s out of %s (%s percent)" % (con_current,con_max,percent), perfdata)
    elif percent > warn:
        return (1, "Much connections: %s out of %s (%s percent)" % (con_current,con_max,percent), perfdata)
    else:
        return (0, "Connections: %s out of %s (%s percent)" % (con_current,con_max,percent), perfdata)

    return (3, "device unreachable")


check_info["sonicwall_conns"] = {
    "default_levels_variable": "sonicwall_conns_default_levels",
    "parse_function": parse_sonicwall_conns,
    "check_function": check_sonicwall_conns,
    "inventory_function": inventory_sonicwall_conns,
    "service_description": "Connections %s",
    "has_perfdata": True,
    "snmp_scan_function": lambda oid: "sonicwall" in oid(".1.3.6.1.2.1.1.1.0").lower(),
    "snmp_info": (".1.3.6.1.4.1.8741.1.3.1", [OID_END, "1", "2"]),
}

#!/usr/bin/env python3
"""Check for Extreme HiPath WLC clients"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from typing import List

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    startswith,
    register,
    SNMPTree,
    OIDEnd,
    any_of,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import StringTable
from cmk.plugins.lib.wlc_clients import WlcClientsSection, ClientsPerInterface


def parse_extreme_wlc_clients(
    string_table: List[StringTable],
) -> WlcClientsSection[ClientsPerInterface]:
    """parse raw data into genric WLC client section"""
    section: WlcClientsSection[ClientsPerInterface] = WlcClientsSection()
    ssids = {}
    for ssid_name, ssid_index in string_table[0]:
        ssids[ssid_index] = ssid_name

    for num_clients_str, ssid_index in string_table[1]:
        num_clients = int(num_clients_str)
        section.total_clients += num_clients
        ssid_name = ssids.get(ssid_index)
        if not ssid_name:
            continue
        if ssid_name not in section.clients_per_ssid:
            section.clients_per_ssid[ssid_name] = ClientsPerInterface()
        section.clients_per_ssid[ssid_name].per_interface["wireless"] = num_clients
    return section


DETECT_EXTREM_WLC = any_of(
    startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.4329.15"),
    startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1916.2.294"),
)


register.snmp_section(
    name="extreme_wlc_clients",
    parsed_section_name="wlc_clients",
    detect=DETECT_EXTREM_WLC,
    parse_function=parse_extreme_wlc_clients,
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.4329.15.3.3.4.4.1",
            oids=[
                "4",  # SSID Name
                OIDEnd(),
            ],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.4329.15.3.3.4.5.1",
            oids=["2", OIDEnd()],  # Users per SSID
        ),
    ],
)

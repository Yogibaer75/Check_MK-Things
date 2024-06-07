#!/usr/bin/env python3
'''Aruba instant WLC connected clients'''
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from typing import List

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
    SNMPTree,
    startswith,
    Result,
    Service,
    State,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    StringTable,
    CheckResult,
    DiscoveryResult,
)


def parse_aruba_instant_wlc_connected_clients(string_table: List[StringTable]):
    """parse wlc connected clients"""
    section = {}
    for client_mac, client_name in string_table[0]:
        mac_string = ":".join("%02x" % ord(b) for b in client_mac)
        section.setdefault(mac_string, client_name)
    return section


register.snmp_section(
    name="aruba_instant_wlc_connected_clients",
    detect=startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.14823.1.2.111"),
    parse_function=parse_aruba_instant_wlc_connected_clients,
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.14823.2.3.3.1.2.4.1",
            oids=[
                "1",  # Client MAC
                "5",  # Client Name
            ],
        )
    ],
)


def discover_aruba_instant_wlc_connected_clients(section) -> DiscoveryResult:
    """discover service if data present"""
    if section:
        yield Service()


def check_aruba_instant_wlc_connected_clients(section) -> CheckResult:
    """check the numbe of connected clients"""
    if not section:
        yield Result(state=State(0), summary="No clients connected")
    else:
        num_clients = 0
        extended_message = []
        for key, data in section.items():
            num_clients += 1
            extended_message.append(f"Client: {data}, MAC: {key}")

        notice = "\n".join(extended_message)
        yield Result(state=State(0), summary=f"{num_clients} connected")
        yield Result(state=State(0), notice=notice)


register.check_plugin(
    name="aruba_instant_wlc_connected_clients",
    service_name="Connected Clients",
    discovery_function=discover_aruba_instant_wlc_connected_clients,
    check_function=check_aruba_instant_wlc_connected_clients,
)

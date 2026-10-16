#!/usr/bin/env python3
"""Aruba instant WLC connected clients"""
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from __future__ import annotations

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    SNMPSection,
    SNMPTree,
    State,
    StringTable,
    any_of,
    startswith,
)

PHYSICAL_AP_SYSOBJECT_ID = ".1.3.6.1.4.1.14823.1.2.87"


def _cluster_services_allowed(sysobject_id: str, ap_count: int) -> bool:
    """Allow cluster data on a physical AP only when it is standalone."""
    is_physical_ap = sysobject_id == PHYSICAL_AP_SYSOBJECT_ID or sysobject_id.startswith(
        f"{PHYSICAL_AP_SYSOBJECT_ID}."
    )
    return not is_physical_ap or ap_count == 1


def parse_aruba_instant_wlc_connected_clients(
    string_table: list[StringTable],
) -> dict[str, str] | None:
    """parse wlc connected clients"""
    sysobject_table, ap_table, clients_table = string_table
    sysobject_id = sysobject_table[0][0] if sysobject_table and sysobject_table[0] else ""

    if not _cluster_services_allowed(sysobject_id, len(ap_table)):
        return None

    section: dict[str, str] = {}
    for client_mac, client_name in clients_table:
        mac_string = ":".join(f"{ord(b):02x}" for b in client_mac)
        section.setdefault(mac_string, client_name)
    return section


snmp_section_aruba_instant_wlc_connected_clients = SNMPSection(
    name="aruba_instant_wlc_connected_clients",
    detect=any_of(
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.14823.1.2.111"),
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.14823.1.2.71"),
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.14823.1.2.137"),
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.14823.1.2.161"),
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.14823.1.2.134"),
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.14823.1.2.87"),
    ),
    parse_function=parse_aruba_instant_wlc_connected_clients,
    fetch=[
        SNMPTree(
            base=".1.3.6.1.2.1.1",
            oids=["2.0"],  # sysObjectID
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.14823.2.3.3.1.2.1.1",
            oids=["2"],  # aiAPName
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.14823.2.3.3.1.2.4.1",
            oids=[
                "1",  # Client MAC
                "5",  # Client Name
            ],
        ),
    ],
)


def discover_aruba_instant_wlc_connected_clients(section: dict[str, str]) -> DiscoveryResult:
    """discover service if data present"""
    if section:
        yield Service()


def check_aruba_instant_wlc_connected_clients(section: dict[str, str]) -> CheckResult:
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


check_plugin_aruba_instant_wlc_connected_clients = CheckPlugin(
    name="aruba_instant_wlc_connected_clients",
    service_name="Connected Clients",
    discovery_function=discover_aruba_instant_wlc_connected_clients,
    check_function=check_aruba_instant_wlc_connected_clients,
)

#!/usr/bin/env python3
"""Aruba Instant WLAN associated clients per access point."""
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from __future__ import annotations

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from collections import Counter

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
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


def parse_aruba_instant_wlc_ap_clients(
    string_table: list[StringTable],
) -> dict[str, int] | None:
    """Count client associations by AP hostname."""
    sysobject_table, ap_table, clients_table = string_table
    sysobject_id = sysobject_table[0][0] if sysobject_table and sysobject_table[0] else ""

    if not _cluster_services_allowed(sysobject_id, len(ap_table)):
        return None

    return dict(Counter(ap_name for (ap_name,) in clients_table if ap_name))


snmp_section_aruba_instant_wlc_ap_clients = SNMPSection(
    name="aruba_instant_wlc_ap_clients",
    detect=any_of(
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.14823.1.2.71"),
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.14823.1.2.87"),
    ),
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
            base=".1.3.6.1.4.1.14823.2.3.3.1.2.5.1",
            oids=["4"],  # Associated AP hostname
        ),
    ],
    parse_function=parse_aruba_instant_wlc_ap_clients,
)


def discover_aruba_instant_wlc_ap_clients(
    section: dict[str, int],
) -> DiscoveryResult:
    for ap_name in section:
        yield Service(item=ap_name)


def check_aruba_instant_wlc_ap_clients(
    item: str,
    section: dict[str, int],
) -> CheckResult:
    if item not in section:
        yield Result(
            state=State.UNKNOWN,
            summary="AP not present in client association table",
        )
        return

    count = section[item]

    yield Result(
        state=State.OK,
        summary=f"{count} connected clients",
    )
    yield Metric("clients", count)


check_plugin_aruba_instant_wlc_ap_clients = CheckPlugin(
    name="aruba_instant_wlc_ap_clients",
    service_name="AP Clients %s",
    discovery_function=discover_aruba_instant_wlc_ap_clients,
    check_function=check_aruba_instant_wlc_ap_clients,
)

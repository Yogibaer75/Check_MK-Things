#!/usr/bin/env python3
"""Check for SophosXG HA state"""

# (c) Matthias Binder 'hds@kpc.de' - K&P Computer Service- und Vertriebs-GmbH
# (c) Andreas Doehler 'andreas.doehler@bechtle.com'
# License: GNU General Public License v2

from typing import Dict, Optional

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    State,
    StringTable,
    all_of,
    exists,
    startswith,
)

Section = Dict[str, str]


def parse_sophosxg_hastate(string_table: StringTable) -> Optional[Section]:
    """parse raw snmp data to dictionary"""
    ha_values: list[str] = [
        "hastatus",
        "currentappkey",
        "peerappkey",
        "currenthastatus",
        "peerhastatus",
        "haconfigmode",
        "laodbalancing",
        "haport",
    ]
    try:
        parsed = {}
        for x in range(8):
            parsed.setdefault(ha_values[x], string_table[0][x])
        return parsed
    except IndexError:
        return {}


snmp_section_sophosxg_hastate = SimpleSNMPSection(
    name="sophosxg_hastate",
    parse_function=parse_sophosxg_hastate,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.2604.5.1.4",
        oids=[
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
        ],
    ),
    detect=all_of(
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.2604.5"),
        exists(".1.3.6.1.4.1.2604.5.1.1.*"),
    ),
)


def discover_sophosxg_hastate(section: Section) -> DiscoveryResult:
    """if data is present return a service"""
    if section:
        yield Service()


def check_sophosxg_hastate(section: Section) -> CheckResult:
    """check the ha state"""
    hastate = section.get("hastatus")
    haloadbalancing = section.get("laodbalancing")
    haport = section.get("haport")

    ha_mode: Dict[str, tuple[str, int]] = {
        "0": ("Disabled", 2),
        "1": ("Enabled", 0),
    }
    lb_mode: Dict[str, str] = {
        "0": "Not Applicable",
        "1": "Loadbalance Off",
        "2": "Loadbalance On",
    }

    hastatename, state = ha_mode.get(hastate, ("Unknown", 3))
    summarytext = (
        f"HA State: {hastatename}, "
        f"HA Port: {haport}, HA Load Balancing:"
        f" {lb_mode.get(haloadbalancing, 'Unknown')}"
    )

    yield Result(state=State(state), summary=summarytext)


check_plugin_sophosxg_hastate = CheckPlugin(
    name="sophosxg_hastate",
    sections=["sophosxg_hastate"],
    service_name="HA State",
    discovery_function=discover_sophosxg_hastate,
    check_function=check_sophosxg_hastate,
)

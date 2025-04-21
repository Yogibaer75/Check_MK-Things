#!/usr/bin/env python3
"""Check for SophosXG version"""

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


def parse_sophosxg_version(string_table: StringTable) -> Optional[Section]:
    """parse raw snmp data to dictionary"""
    info_values: list[str] = [
        "name",
        "type",
        "fwversion",
        "appkey",
        "webcatversion",
        "ipsversion",
    ]
    try:
        parsed = {}
        for x in range(6):
            parsed.setdefault(info_values[x], string_table[0][x])
        return parsed
    except IndexError:
        return {}


snmp_section_sophosxg_version = SimpleSNMPSection(
    name="sophosxg_version",
    parse_function=parse_sophosxg_version,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.2604.5.1.1",
        oids=[
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
        ],
    ),
    detect=all_of(
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.2604.5"),
        exists(".1.3.6.1.4.1.2604.5.1.1.*"),
    ),
)


def discover_sophosxg_version(section: Section) -> DiscoveryResult:
    """if data is present return a service"""
    if section:
        yield Service()


def check_sophosxg_version(params: Dict[str, str], section: Section) -> CheckResult:
    """check the version of the firmware"""
    if not section:
        return
    firmware_check = params.get("firmware_check")

    summarytext = (
        f"Device Name: {section.get('name')}, " f"Device Type: {section.get('type')}"
    )
    yield Result(state=State.OK, summary=summarytext)

    state = 0
    expected_version = ""
    if firmware_check and (firmware_check != section.get("fwversion", "Unknown")):
        state = 1
        expected_version = f" expected version {firmware_check}"
    summarytext = f"Firmware version: {section.get('fwversion')}{expected_version}"
    yield Result(state=State(state), summary=summarytext)

    summarydetails = (
        f"Device App Key: {section.get('appkey')}\n"
        f"Webcat Version: {section.get('webcatversion')}\n"
        f"IPS Version: {section.get('ipsversion')}"
    )

    yield Result(state=State.OK, notice="More Info in details", details=summarydetails)


check_plugin_sophosxg_version = CheckPlugin(
    name="sophosxg_version",
    service_name="Sophos Version",
    discovery_function=discover_sophosxg_version,
    check_function=check_sophosxg_version,
    check_default_parameters={},
    check_ruleset_name="sophosxg_version",
)

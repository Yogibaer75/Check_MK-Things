#!/usr/bin/env python3
"""check for Fan status of Aruba CX 6k switches"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from typing import Any, Dict, Optional

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    OIDEnd,
    Result,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    State,
    StringTable,
)

from cmk_addons.plugins.aruba_cx_sensors.lib import DETECT_ARUBA_CX

Section = Dict[str, Any]


def parse_arbua_cx_fan(string_table: StringTable) -> Optional[Section]:
    """parse raw snmp data to dictionary"""
    try:
        parsed = {}
        for line in string_table:
            parsed.setdefault(line[1], {"state": line[2], "rpm": int(line[3])})
        return parsed
    except IndexError:
        return {}


def discovery_arbua_cx_fan(section: Section) -> DiscoveryResult:
    """every key of the parsed data is found as a service"""
    for key in section.keys():
        if section[key].get("state") == "empty":
            continue
        yield Service(item=key)


def check_arbua_cx_fan(item, section: Section) -> CheckResult:
    """check the status of the Fan"""
    data = section.get(item)
    if not data:
        return

    if data.get("state") != "ok":
        yield Result(state=State.WARN, summary=f"Status not ok --> {data.get('state')}")
    else:
        yield Result(state=State.OK, summary=f"Status is {data.get('state')}")

    if data.get("rpm") != 0:
        yield Metric(name="rpm", value=data.get("rpm", 0))


snmp_section_aruba_cx_fan = SimpleSNMPSection(
    name="arbua_cx_fan",
    parse_function=parse_arbua_cx_fan,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.47196.4.1.1.3.11.5.1.1",
        oids=[
            OIDEnd(),
            "4",
            "5",
            "8",
        ],
    ),
    detect=DETECT_ARUBA_CX,
)

check_plugin_aruba_cx_fan = CheckPlugin(
    name="arbua_cx_fan",
    service_name="Fan %s",
    discovery_function=discovery_arbua_cx_fan,
    check_function=check_arbua_cx_fan,
)

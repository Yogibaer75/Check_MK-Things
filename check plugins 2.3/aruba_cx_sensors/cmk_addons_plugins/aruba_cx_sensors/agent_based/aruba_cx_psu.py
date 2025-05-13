#!/usr/bin/env python3
"""check for PSU status of Aruba CX 6k switches"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from typing import Any, Dict, Optional

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    OIDEnd,
    Result,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    State,
    StringTable,
    check_levels,
)

from cmk_addons.plugins.aruba_cx_sensors.lib import DETECT_ARUBA_CX

Section = Dict[str, Any]


def parse_arbua_cx_psu(string_table: StringTable) -> Optional[Section]:
    """parse raw snmp data to dictionary"""
    try:
        parsed = {}
        for line in string_table:
            parsed.setdefault(
                line[1], {"state": line[2], "watt": int(line[3]), "maxp": int(line[4])}
            )
        return parsed
    except IndexError:
        return {}


def discovery_arbua_cx_psu(section: Section) -> DiscoveryResult:
    """every key of the parsed data is found as a service"""
    for key in section.keys():
        yield Service(item=key)


def check_arbua_cx_psu(item, section: Section) -> CheckResult:
    """check the status of the PSU"""
    data = section.get(item)
    if not data:
        return

    if data.get("state") != "ok":
        yield Result(state=State.WARN, summary=f"Status not ok --> {data.get('state')}")
    else:
        yield Result(state=State.OK, summary=f"Status is {data.get('state')}")

    if data.get("watt") != 0:
        yield from check_levels(
            value=data.get("watt"),
            levels_upper=("fixed", (data.get("maxp"), data.get("maxp"))),
            metric_name="power",
            label="Wattage",
            render_func=lambda x: f"{x:.2f}W",
        )


snmp_section_aruba_cx_psu = SimpleSNMPSection(
    name="arbua_cx_psu",
    parse_function=parse_arbua_cx_psu,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.47196.4.1.1.3.11.2.1.1",
        oids=[
            OIDEnd(),
            "3",
            "4",
            "7",
            "8",
        ],
    ),
    detect=DETECT_ARUBA_CX,
)

check_plugin_aruba_cx_fan = CheckPlugin(
    name="arbua_cx_psu",
    service_name="PSU %s",
    discovery_function=discovery_arbua_cx_psu,
    check_function=check_arbua_cx_psu,
)

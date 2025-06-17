#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Mapping, NamedTuple

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
    startswith,
)
from cmk.plugins.lib.netextreme import DETECT_NETEXTREME

DETECT_VSP = all_of(
    startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1916.2.325"),
    startswith(".1.3.6.1.2.1.1.1.0", "VSP-74"),
)


class PSU(NamedTuple):
    state: int


Section = Mapping[str, PSU]


def parse_extreme_vsp_psu(string_table: StringTable) -> Section:
    return {
        f"{entry[0]}": PSU(
            state=int(entry[1]),
        )
        for entry in string_table
    }


snmp_section_extreme_vsp_psu = SimpleSNMPSection(
    name="extreme_vsp_psu",
    detect=DETECT_NETEXTREME,
    parse_function=parse_extreme_vsp_psu,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.2272.1.4.8.1.1",
        oids=[
            "1",  # id
            "2",  # status
        ],
    ),
)


VSP_PSU_STATE = {
    1: (3, "status can not be determined"),
    2: (1, "power supply not installed"),
    3: (0, "present and supplying power"),
    4: (2, "present, but failure indicated"),
}


def discover_extreme_vsp_psu(section: Section) -> DiscoveryResult:
    for item, entry in section.items():
        if entry.state != 2:
            yield Service(item=item)


def check_extreme_vsp_psu(item: str, section: Section) -> CheckResult:
    psu = section.get(item)
    if not psu:
        return

    status, msg = VSP_PSU_STATE.get(psu.state, (3, "Unknown"))

    yield Result(state=State(status), summary=msg)


check_plugin_extreme_vsp_psu = CheckPlugin(
    name="extreme_vsp_psu",
    service_name="PSU %s",
    discovery_function=discover_extreme_vsp_psu,
    check_function=check_extreme_vsp_psu,
)

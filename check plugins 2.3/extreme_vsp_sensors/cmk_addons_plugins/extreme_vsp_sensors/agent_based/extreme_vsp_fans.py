#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Mapping, NamedTuple

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
    all_of,
    startswith,
)
from cmk.plugins.lib.netextreme import DETECT_NETEXTREME

DETECT_VSP = all_of(
    startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1916.2.325"),
    startswith(".1.3.6.1.2.1.1.1.0", "VSP-74"),
)


class FAN(NamedTuple):
    state: int
    ident: str
    speed: int


Section = Mapping[str, FAN]


def parse_extreme_vsp_fans(string_table: StringTable) -> Section:
    return {
        f"{entry[1]}": FAN(
            state=int(entry[2]),
            ident=entry[0],
            speed=int(entry[3]),
        )
        for entry in string_table
    }


snmp_section_extreme_vsp_fans = SimpleSNMPSection(
    name="extreme_vsp_fans",
    detect=DETECT_NETEXTREME,
    parse_function=parse_extreme_vsp_fans,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.2272.1.101.1.1.4.1",
        oids=[
            OIDEnd(),
            "3",  # name
            "4",  # status
            "5",  # speed
        ],
    ),
)


VSP_FAN_STATE = {
    1: (3, "status can not be determined"),
    2: (0, "present and supplying cooling"),
    3: (2, "present, but failure indicated"),
}


def discover_extreme_vsp_fans(section: Section) -> DiscoveryResult:
    for item, entry in section.items():
        yield Service(item=item)


def check_extreme_vsp_fans(item: str, section: Section) -> CheckResult:
    fan = section.get(item)
    if not fan:
        return

    status, msg = VSP_FAN_STATE.get(fan.state, (3, "Unknown"))

    yield Result(state=State(status), summary=msg)


check_plugin_extreme_vsp_fans = CheckPlugin(
    name="extreme_vsp_fans",
    service_name="FAN %s",
    discovery_function=discover_extreme_vsp_fans,
    check_function=check_extreme_vsp_fans,
)

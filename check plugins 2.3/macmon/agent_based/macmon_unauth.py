#!/usr/bin/env python3
"""check for unauth device"""
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from typing import NamedTuple, List

from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
    StringTable,
)

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
    Result,
    State,
    Service,
)


class MacMonUnAuth(NamedTuple):
    """one unauth device"""

    mac: str
    date: str
    device: str
    index: str


Section = List[MacMonUnAuth]


def parse_macmon_unauth(string_table: StringTable) -> Section:
    """parse string table into named tuple"""
    return [
        MacMonUnAuth(mac, date, device, index)
        for mac, date, device, index in string_table
    ]


register.agent_section(
    name="macmon_unauth",
    parse_function=parse_macmon_unauth,
)


def discover_macmon_unauth(section: Section) -> DiscoveryResult:
    """if data exists discover service"""
    if section:
        yield Service()


def check_macmon_unauth(section: Section) -> CheckResult:
    """check for unauth devices"""
    detailstext = [
        "<table><tr><th>MAC</th><th></th><th>Last seen</th>"
        "<th></th><th>Device</th><th></th><th>Port</th></tr>"
    ]
    num_devices = len(section)
    messagetext = f"{num_devices} Unauth Devices found"

    for line in section:
        detailstext += [
            f"<tr><td>{line.mac}</td><td></td>"
            f"<td>{line.date}</td><td></td>"
            f"<td>{line.device}</td><td></td>"
            f"<td>{line.index}</td></tr>"
        ]

    detailstext += ["</table>\n"]

    status = 0

    if num_devices > 0:
        status = 1

    yield Result(state=State(status), summary=messagetext, details="".join(detailstext))


register.check_plugin(
    name="macmon_unauth",
    service_name="Unauthorized Devices",
    discovery_function=discover_macmon_unauth,
    check_function=check_macmon_unauth,
)

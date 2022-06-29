#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

from typing import Mapping, NamedTuple
from .agent_based_api.v1 import (
    all_of,
    startswith,
    register,
    Result,
    Service,
    SNMPTree,
    State,
)
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, StringTable

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


register.snmp_section(
    name="extreme_vsp_psu",
    detect=DETECT_VSP,
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


register.check_plugin(
    name="extreme_vsp_psu",
    service_name="PSU %s",
    discovery_function=discover_extreme_vsp_psu,
    check_function=check_extreme_vsp_psu,
)

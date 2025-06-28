#!/usr/bin/env python3
"""check for HPE 3Par physical disk status"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

# Example output from agent:
# <<<3par_pd>>>
#  0 0:0:0   FC    10 normal    838656   327680 1:0:1* 0:0:1           900
#  1 0:1:0   FC    10 normal    838656   328704 1:0:1  0:0:1*          900
#  2 0:2:0   FC    10 normal    838656   327680 1:0:1* 0:0:1           900

# The names of the columns are:
#                            -----Size(MB)----- ----Ports----
# Id CagePos Type RPM State      Total     Free A      B      Capacity(GB)

from typing import Mapping
from attr import dataclass
from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    StringTable,
)


@dataclass(frozen=True)
class ThreeParPD:
    """one ps"""

    disk_id: str
    position: str
    con_type: str
    rpm: str
    state: str
    size_mb: str
    free_mb: str
    port_a: str
    port_b: str
    capacity: str


Section = Mapping[str, ThreeParPD]


def parse_3par_pd(string_table: StringTable) -> Section:
    """parse raw data into dict"""
    parsed: dict[str, ThreeParPD] = {}
    for line in string_table:
        if len(line) == 10 and line[0].isdigit():
            parsed.setdefault(
                line[0].zfill(3),
                ThreeParPD(
                    line[0],
                    line[1],
                    line[2],
                    line[3],
                    line[4],
                    line[5],
                    line[6],
                    line[7],
                    line[8],
                    line[9]
                ),
            )
    return parsed


agent_section_3par_pd = AgentSection(
    name="3par_pd",
    parse_function=parse_3par_pd,
    parsed_section_name="3par_pd",
)


def discovery_3par_pd(section: Section) -> DiscoveryResult:
    """if data is present return one service per physical disk"""
    if section:
        for element in section:
            yield Service(item=element)


def check_3par_pd(item: str, section: Section) -> CheckResult:
    """check the pd state"""
    data = section.get(item)
    if not data:
        return

    message = (
        f"Disk {item} ({data.capacity} GB/{data.con_type}) with "
        f"position {data.position} is {data.state}"
    )
    if data.state == "normal":
        yield Result(state=State.OK, summary=message)
    else:
        yield Result(state=State.CRIT, summary=message + "(!!)")


check_plugin_3par_pd = CheckPlugin(
    name="3par_pd",
    service_name="Disk %s",
    sections=["3par_pd"],
    discovery_function=discovery_3par_pd,
    check_function=check_3par_pd,
)

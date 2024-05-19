#!/usr/bin/env python3
"""check for HPE 3Par power supply status"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

# Example output from agent:
# <<<3par_ps:sep(58)>>>
# 0,1  0  726237-001 5DNSFA2438A298 OK      OK      OK
# 0,1  1  726237-001 5DNSFA2438A1EE OK      OK      OK

# The names of the columns are:
# Node PS -Assy_Part- -Assy_Serial-- ACState DCState PSState

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
class ThreeParPS:
    """one ps"""

    part_nr: str
    part_serial: str
    acstate: str
    dcstate: str
    psstate: str


Section = Mapping[str, ThreeParPS]


def parse_3par_ps(string_table: StringTable) -> Section:
    """parse raw data into dict"""
    parsed: dict[str, ThreeParPS] = {}
    for line in string_table:
        if len(line) == 7 and line[0].isdigit():
            for (
                node_id,
                ps_id,
                part_nr,
                part_serial,
                acstate,
                dcstate,
                psstate,
            ) in line:
                parsed.setdefault(
                    f"{node_id}{ps_id}".replace(",", "_"),
                    ThreeParPS(
                        part_nr,
                        part_serial,
                        acstate,
                        dcstate,
                        psstate,
                    ),
                )
    return parsed


agent_section_3par_ps = AgentSection(
    name="3par_ps",
    parse_function=parse_3par_ps,
    parsed_section_name="3par_ps",
)


def discovery_3par_ps(section: Section) -> DiscoveryResult:
    """if data is present return one service per psu"""
    if section:
        for element in section:
            yield Service(item=element)


def check_3par_ps(item: str, section: Section) -> CheckResult:
    """check the ps state"""
    data = section.get(item)
    if not data:
        return

    message = f"PowerSupply {item} is {data.psstate}"
    if data.psstate == "OK":
        yield Result(state=State.OK, summary=message)
    else:
        yield Result(state=State.CRIT, summary=message + "(!!)")


check_plugin_3par_vv = CheckPlugin(
    name="3par_ps",
    service_name="PS %s",
    sections=["3par_ps"],
    discovery_function=discovery_3par_ps,
    check_function=check_3par_ps,
)

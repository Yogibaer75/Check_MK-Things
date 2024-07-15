#!/usr/bin/env python3
"""check for HPE 3Par cage status"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

# Example output from agent:
# <<<3par_cage:sep(32)>>>
# 0 1687417-0 OK      Yes    Yes       Unknown      GreenBlnk   16384    8192          100
# 1 1687417-1 OK      No     Yes       Unknown      GreenBlnk   16384    8192          100

# The names of the columns are:
#                                                               Control    Data        Cache
# Node --Name--- -State- Master InCluster -Service_LED ---LED--- Mem(MB) Mem(MB) Available(%)

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
    get_value_store,
)

from cmk.plugins.lib.temperature import (
    check_temperature,
    TempParamDict,
)


@dataclass(frozen=True)
class ThreeParCage:
    """one cage"""

    name: str
    loopa: str
    posa: str
    loopb: str
    posb: str
    drives: str
    temp: str
    reva: str
    revb: str
    model: str
    side: str


Section = Mapping[str, ThreeParCage]


def parse_3par_cage(string_table: StringTable) -> Section:
    """parse raw data into dict"""
    parsed: dict[str, ThreeParCage] = {}
    for line in string_table:
        if len(line) == 12 and line[0].isdigit():
            for (
                cage_id,
                name,
                loopa,
                posa,
                loopb,
                posb,
                drives,
                temp,
                reva,
                revb,
                model,
                side,
            ) in line:
                parsed.setdefault(
                    cage_id,
                    ThreeParCage(
                        name,
                        loopa,
                        posa,
                        loopb,
                        posb,
                        drives,
                        temp,
                        reva,
                        revb,
                        model,
                        side,
                    ),
                )
    return parsed


agent_section_3par_cage = AgentSection(
    name="3par_cage",
    parse_function=parse_3par_cage,
    parsed_section_name="3par_cage",
)


def discovery_3par_cage(section: Section) -> DiscoveryResult:
    """id data is present return one service per cage"""
    if section:
        for element in section:
            yield Service(item=element)


def check_3par_cage(item: str, params: TempParamDict, section: Section) -> CheckResult:
    """check the cage state"""
    data = section.get(item)
    if not data:
        return

    temperatures = data.get("temp").split("-")
    yield from check_temperature(
        temperatures[1],
        params,
        unique_name=f"3par_cage_temp_{item}",
        value_store=get_value_store(),
    )
    message = (
        f"Cage {data.get('cage_id')} with {data.get('drives')} Drives is Available"
    )
    yield Result(state=State.OK, summary=message)


check_plugin_3par_cage = CheckPlugin(
    name="3par_cage",
    service_name="Cage %s",
    sections=["3par_cage"],
    discovery_function=discovery_3par_cage,
    check_function=check_3par_cage,
    check_ruleset_name="temperature",
    check_default_parameters={},
)

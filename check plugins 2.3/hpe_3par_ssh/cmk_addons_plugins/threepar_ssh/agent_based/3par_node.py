#!/usr/bin/env python3
"""check for HPE 3Par node status"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

# Example output from agent:
# <<<3par_node:sep(32)>>>
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
)


@dataclass(frozen=True)
class ThreeParNode:
    """one ps"""

    node_id: str
    name: str
    state: str
    master: str
    cluster: str
    service_led: str
    master_led: str
    control_mem: str
    data_mem: str
    cache: str


Section = Mapping[str, ThreeParNode]


def parse_3par_node(string_table: StringTable) -> Section:
    """parse raw data into dict"""
    parsed: dict[str, ThreeParNode] = {}
    for line in string_table:
        if len(line) == 10 and line[0].isdigit():
            for (
                node_id,
                name,
                state,
                master,
                cluster,
                service_led,
                master_led,
                control_mem,
                data_mem,
                cache,
            ) in line:
                parsed.setdefault(
                    node_id,
                    ThreeParNode(
                        name,
                        state,
                        master,
                        cluster,
                        service_led,
                        master_led,
                        control_mem,
                        data_mem,
                        cache,
                    ),
                )
    return parsed


agent_section_3par_node = AgentSection(
    name="3par_node",
    parse_function=parse_3par_node,
    parsed_section_name="3par_node",
)


def discovery_3par_node(section: Section) -> DiscoveryResult:
    """if data is present return one service per node"""
    if section:
        for element in section:
            yield Service(item=element)


def check_3par_node(item: str, section: Section) -> CheckResult:
    """check the pd state"""
    data = section.get(item)
    if not data:
        return

    message = f"Node {item} with name {data.name} is {data.state}"
    if data.state == "OK":
        yield Result(state=State.OK, summary=message)
    else:
        yield Result(state=State.CRIT, summary=message + "(!!)")


check_plugin_3par_node = CheckPlugin(
    name="3par_node",
    service_name="Node %s",
    sections=["3par_node"],
    discovery_function=discovery_3par_node,
    check_function=check_3par_node,
)

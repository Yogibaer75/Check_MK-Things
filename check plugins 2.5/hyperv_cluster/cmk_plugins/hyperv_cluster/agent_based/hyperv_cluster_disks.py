#!/usr/bin/python

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.agent_based.v2 import (  # type: ignore[import]
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)
from cmk.plugins.hyperv_cluster.lib import parse_hyperv

Section = dict[str, dict[str, str]]

def discovery_hyperv_cluster_disks(section: Section) -> DiscoveryResult:
    for disk in section:
        yield Service(item=disk)


def check_hyperv_cluster_disks(item: str, section: Section) -> CheckResult:

    disk = section.get(item, {})

    if not disk:
        yield Result(state=State(3), summary="Disk not found in agent output")
        return

    state = 0
    if disk.get("cluster.disk.state") != "Online":
        state = 3
    message = (
        f"is {disk.get('cluster.disk.state')}, with owner {disk.get('cluster.disk.owner_node')}"
        f" and group {disk.get('cluster.disk.owner_group')}."
    )
    yield Result(state=State(state), summary=message)


agent_section_hyperv_cluster_disks = AgentSection(
    name="hyperv_cluster_disks",
    parse_function=parse_hyperv,
)

check_plugin_hyperv_cluster_disks = CheckPlugin(
    name="hyperv_cluster_disks",
    service_name="HyperV Disk %s",
    sections=["hyperv_cluster_disks"],
    discovery_function=discovery_hyperv_cluster_disks,
    check_function=check_hyperv_cluster_disks,
)

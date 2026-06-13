#!/usr/bin/python

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk_addons.plugins.hyperv.lib import parse_hyperv

from cmk.agent_based.v2 import (  # type: ignore[import]
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)


def discovery_hyperv_cluster_disks(section) -> DiscoveryResult:
    for disk in section.keys():
        yield Service(item=disk)


def check_hyperv_cluster_disks(item: str, section) -> CheckResult:

    disk = section.get(item, "")

    if not disk:
        yield Result(state=State(3), summary="Disk not found in agent output")
        return

    state = 0
    if disk["cluster.disk.state"] != "Online":
        state = 3
    message = (
        f"is {disk['cluster.disk.state']}, with owner {disk['cluster.disk.owner_node']}"
        f"and group {disk['cluster.disk.owner_group']}."
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

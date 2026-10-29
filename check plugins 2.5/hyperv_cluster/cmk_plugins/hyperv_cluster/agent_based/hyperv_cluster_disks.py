#!/usr/bin/python

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)
from cmk.plugins.hyperv_cluster.lib import parse_hyperv, Section

_DISK_STATES = {
    "Online": State.OK,
    "Initializing": State.WARN,
    "Pending": State.WARN,
    "OnlinePending": State.WARN,
    "OfflinePending": State.WARN,
    "Offline": State.CRIT,
    "Failed": State.CRIT,
}


def discover_hyperv_cluster_disks(section: Section) -> DiscoveryResult:
    for disk in section:
        yield Service(item=disk)


def check_hyperv_cluster_disks(item: str, section: Section) -> CheckResult:
    if (disk := section.get(item)) is None:
        return

    state = disk.get("cluster.disk.state") or "not reported"
    yield Result(state=_DISK_STATES.get(state, State.UNKNOWN), summary=f"State: {state}")
    if owner := disk.get("cluster.disk.owner_node"):
        yield Result(state=State.OK, summary=f"Owner: {owner}")
    if group := disk.get("cluster.disk.owner_group"):
        yield Result(state=State.OK, summary=f"Group: {group}")


agent_section_hyperv_cluster_disks = AgentSection(
    name="hyperv_cluster_disks",
    parse_function=parse_hyperv,
)

check_plugin_hyperv_cluster_disks = CheckPlugin(
    name="hyperv_cluster_disks",
    service_name="Hyper-V cluster disk %s",
    discovery_function=discover_hyperv_cluster_disks,
    check_function=check_hyperv_cluster_disks,
)

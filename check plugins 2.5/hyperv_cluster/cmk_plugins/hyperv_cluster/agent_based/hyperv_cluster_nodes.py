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

_NODE_STATES = {
    "Up": State.OK,
    "Paused": State.WARN,
    "Joining": State.WARN,
    "Down": State.CRIT,
}

# Status information of Windows Server 2016 and later. "Normal" and unknown values are OK.
_NODE_STATUS_INFORMATION = {
    "Isolated": State.WARN,
    "Quarantined": State.CRIT,
}


def discover_hyperv_cluster_nodes(section: Section) -> DiscoveryResult:
    for node in section:
        yield Service(item=node)


def check_hyperv_cluster_nodes(item: str, section: Section) -> CheckResult:
    if (node := section.get(item)) is None:
        return

    state = node.get("cluster.node.state") or "not reported"
    yield Result(state=_NODE_STATES.get(state, State.UNKNOWN), summary=f"State: {state}")
    if node_id := node.get("cluster.node.id"):
        yield Result(state=State.OK, summary=f"ID: {node_id}")
    if weight := node.get("cluster.node.weight"):
        yield Result(state=State.OK, summary=f"Weight: {weight}")
    if info := node.get("cluster.node.info"):
        if (info_state := _NODE_STATUS_INFORMATION.get(info, State.OK)) is State.OK:
            yield Result(state=State.OK, notice=f"Status information: {info}")
        else:
            yield Result(state=info_state, summary=f"Status information: {info}")


agent_section_hyperv_cluster_nodes = AgentSection(
    name="hyperv_cluster_nodes",
    parse_function=parse_hyperv,
)

check_plugin_hyperv_cluster_nodes = CheckPlugin(
    name="hyperv_cluster_nodes",
    service_name="Hyper-V cluster node %s",
    discovery_function=discover_hyperv_cluster_nodes,
    check_function=check_hyperv_cluster_nodes,
)

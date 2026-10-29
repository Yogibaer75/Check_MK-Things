#!/usr/bin/python

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from collections.abc import Mapping

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)
from cmk.plugins.hyperv_cluster.lib import merge_node_sections, parse_hyperv, Section

_NETWORK_STATES = {
    "Up": State.OK,
    "Partitioned": State.WARN,
    "Down": State.CRIT,
    "Unavailable": State.CRIT,
}


def discover_hyperv_cluster_network(section: Section) -> DiscoveryResult:
    for network in section:
        yield Service(item=network)


def check_hyperv_cluster_network(item: str, section: Section) -> CheckResult:
    if (network := section.get(item)) is None:
        return

    state = network.get("cluster.network.state") or "not reported"
    yield Result(state=_NETWORK_STATES.get(state, State.UNKNOWN), summary=f"State: {state}")
    if address := network.get("cluster.network.ip"):
        yield Result(state=State.OK, summary=f"Address: {address}")
    if role := network.get("cluster.network.role"):
        yield Result(state=State.OK, summary=f"Role: {role}")


def cluster_check_hyperv_cluster_network(
    item: str, section: Mapping[str, Section | None]
) -> CheckResult:
    yield from check_hyperv_cluster_network(item, merge_node_sections(section))


agent_section_hyperv_cluster_network = AgentSection(
    name="hyperv_cluster_network",
    parse_function=parse_hyperv,
)

check_plugin_hyperv_cluster_network = CheckPlugin(
    name="hyperv_cluster_network",
    service_name="Hyper-V cluster network %s",
    discovery_function=discover_hyperv_cluster_network,
    check_function=check_hyperv_cluster_network,
    cluster_check_function=cluster_check_hyperv_cluster_network,
)

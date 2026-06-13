#!/usr/bin/python

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from typing import Any

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

Section = dict[str, dict[str, Any]]


def discovery_hyperv_cluster_network(section) -> DiscoveryResult:
    for network in section.keys():
        yield Service(item=network)


def check_hyperv_cluster_network(item: str, section: Section) -> CheckResult:

    network = section.get(item, {})

    if not network:
        yield Result(state=State(3), summary="Network not found in agent output")

    state = 0
    if network.get("cluster.network.state") != "Up":
        state = 3
    message = (
        f"is {network.get('cluster.network.state')}, "
        f"has address {network.get('cluster.network.ip')} and "
        f"role {network.get('cluster.network.role')}."
    )
    yield Result(state=State(state), summary=message)


agent_section_hyperv_cluster_network = AgentSection(
    name="hyperv_cluster_network",
    parse_function=parse_hyperv,
)

check_plugin_hyperv_cluster_network = CheckPlugin(
    name="hyperv_cluster_network",
    service_name="HyperV Network %s",
    sections=["hyperv_cluster_network"],
    discovery_function=discovery_hyperv_cluster_network,
    check_function=check_hyperv_cluster_network,
)

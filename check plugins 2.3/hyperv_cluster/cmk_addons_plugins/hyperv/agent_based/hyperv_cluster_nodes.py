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


def discovery_hyperv_cluster_nodes(section) -> DiscoveryResult:
    for node in section.keys():
        yield Service(item=node)


def check_hyperv_cluster_nodes(item: str, section: Section) -> CheckResult:

    node = section.get(item, {})

    if not node:
        yield Result(state=State(3), summary="Node not found in agent output")

    state = 0
    if node.get("cluster.node.state") != "Up":
        state = 3
    message = (
        f"is {node.get('cluster.node.state')}, "
        f"has ID {node.get('cluster.node.id')} and "
        f"weight {node.get('cluster.node.weight')}."
    )
    yield Result(state=State(state), summary=message)


agent_section_hyperv_cluster_nodes = AgentSection(
    name="hyperv_cluster_nodes",
    parse_function=parse_hyperv,
)

check_plugin_hyperv_cluster_nodes = CheckPlugin(
    name="hyperv_cluster_nodes",
    service_name="HyperV Node %s",
    sections=["hyperv_cluster_nodes"],
    discovery_function=discovery_hyperv_cluster_nodes,
    check_function=check_hyperv_cluster_nodes,
)

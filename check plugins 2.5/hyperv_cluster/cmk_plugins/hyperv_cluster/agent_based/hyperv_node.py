#!/usr/bin/python

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    HostLabel,
    HostLabelGenerator,
    Result,
    Service,
    State,
)
from cmk.plugins.hyperv_cluster.lib import parse_hyperv_json

Section = dict[str, Mapping[str, Any]]


def host_label_hyperv_node(section: Section) -> HostLabelGenerator:
    if section:
        yield HostLabel("cmk/hyperv_object", "server")


def discovery_hyperv_node(section) -> DiscoveryResult:
    if section:
        yield Service()


def check_hyperv_node(section: Section) -> CheckResult:
    if section:
        name = section.get("host", "")
        count = section.get("vmCount", "")

        message = f"Hyper-V Node {name} has {count} VMs."

        yield Result(state=State(0), summary=message)


agent_section_hyperv_node_json: AgentSection = AgentSection(
    name="hyperv_node_json",
    parse_function=parse_hyperv_json,
    parsed_section_name="hyperv_node",
    host_label_function=host_label_hyperv_node,
)

check_plugin_hyperv_node = CheckPlugin(
    name="hyperv_node",
    service_name="HyperV Node Status",
    sections=["hyperv_node"],
    discovery_function=discovery_hyperv_node,
    check_function=check_hyperv_node,
)

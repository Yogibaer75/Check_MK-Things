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
from cmk.plugins.hyperv_cluster.lib import hyperv_vm_convert

Section = Mapping[str, str]


def discover_hyperv_cluster_general(section: Section) -> DiscoveryResult:
    if "cluster.name" in section:
        yield Service()


def check_hyperv_cluster_general(section: Section) -> CheckResult:
    yield Result(state=State.OK, summary=f"Name: {section.get('cluster.name', '')}")
    if ip := section.get("cluster.ip"):
        yield Result(state=State.OK, summary=f"IP: {ip}")
    # Quorum types without a witness, e.g. NodeMajority, have no quorum resource
    quorum_type = section.get("quorum.type", "")
    if resource := section.get("quorum.resourcename"):
        yield Result(state=State.OK, summary=f"Quorum: {resource} ({quorum_type})")
    elif quorum_type:
        yield Result(state=State.OK, summary=f"Quorum: {quorum_type}")


def cluster_check_hyperv_cluster_general(section: Mapping[str, Section | None]) -> CheckResult:
    # Every node reports the same cluster. Use the report of the first node.
    for node in sorted(section):
        if node_section := section[node]:
            yield from check_hyperv_cluster_general(node_section)
            return


agent_section_hyperv_cluster_general = AgentSection(
    name="hyperv_cluster_general",
    parse_function=hyperv_vm_convert,
)

check_plugin_hyperv_cluster_general = CheckPlugin(
    name="hyperv_cluster_general",
    service_name="Hyper-V cluster",
    discovery_function=discover_hyperv_cluster_general,
    check_function=check_hyperv_cluster_general,
    cluster_check_function=cluster_check_hyperv_cluster_general,
)

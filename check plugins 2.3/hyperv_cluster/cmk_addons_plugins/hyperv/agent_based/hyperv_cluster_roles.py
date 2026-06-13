#!/usr/bin/python

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from collections.abc import Mapping
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


hyperv_cluster_roles_default_levels = {
    "default_status": "active",
    "match_services": [],
}

states = {
    "active": 0,
    "inactive": 1,
    "Online": 0,
    "Offline": 1,
}


def discovery_hyperv_cluster_roles(section) -> DiscoveryResult:
    """Discovery function"""
    for vm in section.keys():
        yield Service(item=vm)


def check_hyperv_cluster_roles(
    item: str, params: Mapping[str, Any], section: Section
) -> CheckResult:
    """Check function"""
    vm = section.get(item, {})

    translate_state = {
        "active": "Online",
        "inactive": "Offline",
    }

    if not vm:
        return

    state = 0
    wanted_result = None
    wanted_states = params.get("match_services")

    if wanted_states:
        for element in wanted_states:
            if element.get("service_name") == item:
                wanted_state = element.get("state")
                wanted_result = translate_state.get(wanted_state)
                break

    vm_state = vm.get("cluster.vm.state")
    if wanted_result:
        if wanted_result == vm_state:
            message = f"power state: {vm.get("cluster.vm.state")}"
            yield Result(state=State(state), summary=message)
        else:
            state = 1
            message = f"power state: {vm.get("cluster.vm.state")} - wanted state: {wanted_state}"
            yield Result(state=State(state), summary=message)
    else:
        if params.get("default_status") == "ignore":
            state = 0
        else:
            state = states.get(vm.get("cluster.vm.state") or "Unknown", 3)
        message = f"power state: {vm.get("cluster.vm.state")}"
        yield Result(state=State(state), summary=message)

    if vm.get("cluster.vm.owner"):
        if vm.get("cluster.vm.state") == "Online":
            message = f"running on {vm.get("cluster.vm.owner")}"
            yield Result(state=State(0), summary=message)
        else:
            message = f"defined on {vm.get("cluster.vm.owner")}"
            yield Result(state=State(0), summary=message)


def cluster_check_hyperv_cluster_roles(
    item: str, params: Mapping[str, Any], section: Mapping[str, Section | None]
) -> CheckResult:
    """Cluster check function"""
    found = []
    for node, node_section in section.items():
        if not node_section:
            continue
        results = list(check_hyperv_cluster_roles(item, params, node_section))
        if results:
            found.append((node, results[0]))

    if not found:
        yield Result(state=State(3), summary="VM not found on any node")
        return

    best_state = State.best(*(result.state for _node, result in found))
    best_running_on, best_result = [(n, r) for n, r in found if r.state == best_state][
        -1
    ]

    yield best_result
    if best_running_on and best_state != State.CRIT:
        yield Result(state=best_state, summary=f"running on: {best_running_on}")


agent_section_hyperv_cluster_roles = AgentSection(
    name="hyperv_cluster_roles",
    parse_function=parse_hyperv,
)

check_plugin_hyperv_cluster_roles = CheckPlugin(
    name="hyperv_cluster_roles",
    service_name="HyperV VM %s",
    sections=["hyperv_cluster_roles"],
    discovery_function=discovery_hyperv_cluster_roles,
    check_function=check_hyperv_cluster_roles,
    cluster_check_function=cluster_check_hyperv_cluster_roles,
    check_default_parameters=hyperv_cluster_roles_default_levels,
    check_ruleset_name="hyperv_cluster_roles",
)

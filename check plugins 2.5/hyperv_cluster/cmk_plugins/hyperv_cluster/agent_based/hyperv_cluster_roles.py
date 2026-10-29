#!/usr/bin/python

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from collections.abc import Mapping, Sequence
from typing import Literal, TypedDict

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


class RolesParams(TypedDict):
    expected_state: Literal["active", "inactive", "ignore"]


_DEFAULT_PARAMS: RolesParams = {"expected_state": "active"}

_EXPECTED_VM_STATE = {
    "active": "Online",
    "inactive": "Offline",
}

# Known cluster group states that differ from the expected one
_UNEXPECTED_VM_STATES = {"Online", "Offline", "PartialOnline", "Pending"}

_RUNNING_VM_STATES = {"Online", "PartialOnline"}


def discover_hyperv_cluster_roles(section: Section) -> DiscoveryResult:
    for vm in section:
        yield Service(item=vm)


def _vm_state(vm_state: str, expected_state: Literal["active", "inactive", "ignore"]) -> State:
    if vm_state == "Failed":
        return State.CRIT
    if expected_state == "ignore" or vm_state == _EXPECTED_VM_STATE[expected_state]:
        return State.OK
    if vm_state in _UNEXPECTED_VM_STATES:
        return State.WARN
    return State.UNKNOWN


def _check_vm(vm: Mapping[str, str], params: RolesParams) -> Sequence[Result]:
    vm_state = vm.get("cluster.vm.state", "")
    state = _vm_state(vm_state, params["expected_state"])
    summary = f"Power state: {vm_state}"
    if state is State.WARN:
        summary += f" (expected: {_EXPECTED_VM_STATE[params['expected_state']]})"

    if not (owner := vm.get("cluster.vm.owner")):
        location = "Not assigned to a node"
    elif vm_state in _RUNNING_VM_STATES:
        location = f"Running on: {owner}"
    else:
        location = f"Defined on: {owner}"

    return [Result(state=state, summary=summary), Result(state=State.OK, summary=location)]


def check_hyperv_cluster_roles(item: str, params: RolesParams, section: Section) -> CheckResult:
    if (vm := section.get(item)) is not None:
        yield from _check_vm(vm, params)


def cluster_check_hyperv_cluster_roles(
    item: str, params: RolesParams, section: Mapping[str, Section | None]
) -> CheckResult:
    # Every cluster node reports all clustered VMs. Use the most favourable report.
    reports = [
        _check_vm(vm, params)
        for node_section in section.values()
        if node_section is not None and (vm := node_section.get(item)) is not None
    ]
    if not reports:
        return
    worst_states = [State.worst(*(result.state for result in results)) for results in reports]
    yield from reports[worst_states.index(State.best(*worst_states))]


agent_section_hyperv_cluster_roles = AgentSection(
    name="hyperv_cluster_roles",
    parse_function=parse_hyperv,
)

check_plugin_hyperv_cluster_roles = CheckPlugin(
    name="hyperv_cluster_roles",
    service_name="Hyper-V cluster VM %s",
    discovery_function=discover_hyperv_cluster_roles,
    check_function=check_hyperv_cluster_roles,
    cluster_check_function=cluster_check_hyperv_cluster_roles,
    check_ruleset_name="hyperv_cluster_roles",
    check_default_parameters=_DEFAULT_PARAMS,
)

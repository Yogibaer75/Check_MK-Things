#!/usr/bin/python
# # -*- encoding: utf-8; py-indent-offset: 4 -*-

from collections.abc import Mapping
from typing import Any, Dict

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)
from cmk_addons.plugins.hyperv.lib import hyperv_vm_general

Section = Dict[str, Mapping[str, Any]]


def discovery_hyperv_vm_general_name(section: Section) -> DiscoveryResult:
    if section:
        name_found = False
        for key, data in section.items():
            if "name" in data:
                name_found = True
        if name_found:
            yield Service()


def check_hyperv_vm_general_name(section: Section) -> CheckResult:
    for runtime_host, data in section.items():
        if data.get("name"):
            yield Result(state=State(0), summary=f"{data['name']} on {runtime_host}")


agent_section_hyperv_vm_general = AgentSection(
    name="hyperv_vm_general",
    parse_function=hyperv_vm_general,
)

check_plugin_hyperv_vm_general = CheckPlugin(
    name="hyperv_vm_general",
    service_name="HyperV Name",
    sections=["hyperv_vm_general"],
    discovery_function=discovery_hyperv_vm_general_name,
    check_function=check_hyperv_vm_general_name,
)


def discovery_hyperv_vm_general_running_on(section):
    if section:
        runtime_hosts = []
        runtime_states = {}
        for key, data in section.items():
            runtime_hosts.append(key)
            runtime_states[key]=data.get("runtime.powerState", "unknown")
        yield Service(parameters={"runtime_hosts":runtime_hosts, "states":runtime_states})


def check_hyperv_vm_general_running_on(params, section: Section) -> CheckResult:
    if not section:
        yield Result(state=State(3), summary="Runtime host information is missing")
        return

    states = params.get("states", {})
    for runtime_host, data in section.items():
        if not params.get("runtime_hosts") or runtime_host not in params.get("runtime_hosts"):
            yield Result(state=State(1), summary=f"Configured host {runtime_host} unexpected")
            continue
        state = data.get("runtime.powerState", "unknown")

        message = f"Configured on {runtime_host} with state {state}"
        yield Result(state=State(0), summary=message)
        if states:
            if states.get(runtime_host) != state:
                yield Result(state=State(1), summary="changed since last discovery")


check_plugin_hyperv_vm_general_running_on = CheckPlugin(
    name="hyperv_vm_general_running_on",
    service_name="HyperV Hostsystem",
    sections=["hyperv_vm_general"],
    discovery_function=discovery_hyperv_vm_general_running_on,
    check_function=check_hyperv_vm_general_running_on,
    check_default_parameters={},
)

#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# ported to API v4 by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

from collections.abc import Mapping
from typing import Any, TypedDict

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    StringTable,
    render,
)
from cmk.plugins.prism_v4.lib_v4 import parse_by_name

Section = Mapping[str, Mapping[str, Any]]


def parse_prism_hosts_v4(string_table: StringTable) -> Section:
    return parse_by_name(string_table, "hostName")


agent_section_prism_hosts_v4 = AgentSection(
    name="prism_hosts_v4",
    parse_function=parse_prism_hosts_v4,
)


def discovery_prism_hosts_v4(section: Section) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


class CheckParamsPrimsHosts(TypedDict, total=False):
    system_state: str
    acropolis_connection_state: bool


DEFAULT: CheckParamsPrimsHosts = {
    "system_state": "NORMAL",
    "acropolis_connection_state": True,
}


def check_prism_hosts_v4(item: str, params: CheckParamsPrimsHosts, section: Section) -> CheckResult:
    data = section.get(item)
    if not data:
        return
    hypervisor = data.get("hypervisor", {})
    wanted_state = params["system_state"]
    state_text = data.get("nodeStatus", "unknown")

    message = f"has state {state_text}"
    if state_text != wanted_state:
        yield Result(state=State.WARN, summary=message)
        yield Result(state=State.OK, summary=f"expected state {wanted_state}")
    else:
        yield Result(state=State.OK, summary=message)
    yield Result(state=State.OK, summary=f"Number of VMs {hypervisor.get('numberOfVms')}")
    if (memory := data.get("memorySizeBytes")) is not None:
        yield Result(state=State.OK, summary=f"Memory {render.bytes(memory)}")
    if (boottime := data.get("bootTimeUsecs")) is not None:
        yield Result(state=State.OK, summary=f"Boottime {render.datetime(boottime / 1000000.0)}")
    acropolis_state = hypervisor.get("acropolisConnectionState", "")
    yield Result(
        state=(
            State.CRIT
            if acropolis_state == "DISCONNECTED" and params["acropolis_connection_state"]
            else State.OK
        ),
        summary=f"Acropolis state is {acropolis_state}",
    )
    yield from _check_maintenance(data)


def _check_maintenance(data: Mapping[str, Any]) -> CheckResult:
    """Maintenance or HA failover of the node or its CVM is not a failure, but should be seen"""
    if (hypervisor_state := data.get("hypervisor", {}).get("state")) is not None:
        yield Result(
            state=State.OK if hypervisor_state == "ACROPOLIS_NORMAL" else State.WARN,
            summary=f"Hypervisor state: {hypervisor_state}",
        )
    if (maintenance := data.get("maintenanceState")) is not None and maintenance != "normal":
        yield Result(state=State.WARN, summary=f"Node maintenance state: {maintenance}")
    if data.get("controllerVm", {}).get("isInMaintenanceMode"):
        yield Result(state=State.WARN, summary="CVM is in maintenance mode")


check_plugin_prism_hosts_v4 = CheckPlugin(
    name="prism_hosts_v4",
    service_name="NTNX Host %s",
    sections=["prism_hosts_v4"],
    check_default_parameters=DEFAULT,
    discovery_function=discovery_prism_hosts_v4,
    check_function=check_prism_hosts_v4,
    check_ruleset_name="prism_hosts",
)

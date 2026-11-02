#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# ported to API v4 by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

from collections.abc import Mapping
from typing import Any

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
from cmk.plugins.prism_v4.lib_v4 import PRISM_POWER_STATES, parse_by_name

Section = Mapping[str, Mapping[str, Any]]


def parse_prism_vms_v4(string_table: StringTable) -> Section:
    return parse_by_name(string_table)


agent_section_prism_vms_v4 = AgentSection(
    name="prism_vms_v4",
    parse_function=parse_prism_vms_v4,
)


def discovery_prism_vms_v4(section: Section) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_prism_vms_v4(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:
    wanted_state = params.get("system_state", "on")
    data = section.get(item)
    if not data:
        return

    state_text = data.get("powerState", "unknown")
    if wanted_state in ("ignore", state_text.lower()):
        state = 0
    else:
        state = PRISM_POWER_STATES.get(state_text.lower(), 3)

    vm_desc = data.get("description")
    if vm_desc:
        vm_desc = vm_desc.replace("\n", r"\n")
    if "template" in str(vm_desc):
        vm_desc = "Template"

    host_name = data.get("hostName")
    memory = render.bytes(data.get("memorySizeBytes", 0))

    yield Result(state=State(state), summary=f"with status {state_text} - on Host {host_name}")
    yield Result(
        state=State.OK,
        notice=(
            f"Memory {memory},\nDescription {vm_desc},\n"
            f"Protection State {data.get('protectionType')}"
        ),
    )


check_plugin_prism_vms_v4 = CheckPlugin(
    name="prism_vms_v4",
    service_name="NTNX VM %s",
    sections=["prism_vms_v4"],
    check_default_parameters={
        "system_state": "on",
    },
    discovery_function=discovery_prism_vms_v4,
    check_function=check_prism_vms_v4,
    check_ruleset_name="prism_vms",
)

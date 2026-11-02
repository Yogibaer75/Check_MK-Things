#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# ported to API v4 by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    render,
)
from cmk.plugins.prism_v4.lib_v4 import PRISM_POWER_STATES

Section = Mapping[str, Any]


def num_vcpus(vm: Section) -> int:
    return (
        int(vm.get("numSockets", 0))
        * int(vm.get("numCoresPerSocket", 1))
        * int(vm.get("numThreadsPerCore", 1))
    )


def discovery_prism_vm_status_v4(section: Section) -> DiscoveryResult:
    if section:
        yield Service()


def check_prism_vm_status_v4(params: Mapping[str, Any], section: Section) -> CheckResult:
    wanted_state = params.get("system_state", "on")
    if not section:
        return

    power = section.get("powerState", "unknown")
    # power states configured in the rule replace the default mapping
    power_states = {**PRISM_POWER_STATES, **params.get("power_states", {})}
    state_value = power_states.get(power.lower(), params.get("other_power_state", 3))
    running_on = section.get("hostName") or "unknown"
    ram = int(section.get("memorySizeBytes", 0))
    prot_state = section.get("protectionType", "unknown")

    if wanted_state == power.lower() or wanted_state == "ignore":
        state = 0
    else:
        state = state_value

    yield Result(state=State(state), summary=f"is in state {power}, defined on {running_on}")
    yield Result(
        state=State.OK, summary=f"CPUs: {num_vcpus(section)}, Memory: {render.bytes(ram)}"
    )
    # API v4 has no protection domains anymore, only the protection type is left
    yield Result(state=State.OK, notice=f"Protection State: {prot_state}")


check_plugin_prism_vm_status_v4 = CheckPlugin(
    name="prism_vm_status_v4",
    service_name="NTNX VM State",
    sections=["prism_vm_v4"],
    check_default_parameters={
        "system_state": "on",
    },
    discovery_function=discovery_prism_vm_status_v4,
    check_function=check_prism_vm_status_v4,
    check_ruleset_name="prism_vm_status",
)

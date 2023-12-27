#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.agent_based.v2 import CheckPlugin, Result, Service, State
from cmk.agent_based.v2.type_defs import CheckResult, DiscoveryResult
from cmk.plugins.redfish.lib import (
    RedfishAPIData,
    redfish_health_state,
)


def discover_redfish_memory_summary(section: RedfishAPIData) -> DiscoveryResult:
    for element in section:
        if "MemorySummary" in element.keys():
            yield Service()


def check_redfish_memory_summary(section: RedfishAPIData) -> CheckResult:
    data = []
    for element in section:
        data.append(element.get("MemorySummary"))

    if not data:
        return

    for element in data:
        state = element.get("Status", {"Health": "Unknown"})
        result_state, state_text = redfish_health_state(state)
        message = f"Capacity: {element.get('TotalSystemMemoryGiB')}GB, with State: {state_text}"

        yield Result(state=State(result_state), summary=message)


check_plugin_redfish_memory_summary = CheckPlugin(
    name="redfish_memory_summary",
    service_name="Memory Summary",
    sections=["redfish_system"],
    discovery_function=discover_redfish_memory_summary,
    check_function=check_redfish_memory_summary,
)

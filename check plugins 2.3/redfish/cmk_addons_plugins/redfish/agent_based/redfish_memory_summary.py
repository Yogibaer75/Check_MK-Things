#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)
from cmk_addons.plugins.redfish.lib import (
    RedfishAPIData,
    redfish_health_state,
)


def discover_redfish_memory_summary(section: RedfishAPIData) -> DiscoveryResult:
    if len(section) == 1:
        if not list(section.values())[0].get("MemorySummary", {}):
            return
        yield Service(item="Summary")
    else:
        for item, data in section.items():
            if not data.get("MemorySummary", {}):
                continue
            yield Service(item=f"Summary {item}")


def check_redfish_memory_summary(item: str, section: RedfishAPIData) -> CheckResult:
    result = {}
    if len(section) == 1:
        result = list(section.values())[0].get("MemorySummary", {})
    else:
        systemid = item.split(" ")[-1]
        result = section.get(systemid, {}).get("MemorySummary", {})
    if not result:
        return

    state = result.get("Status", {"Health": "Unknown"})
    result_state, state_text = redfish_health_state(state)
    message = f"Capacity: {result.get('TotalSystemMemoryGiB')}GB, with State: {state_text}"

    yield Result(state=State(result_state), summary=message)


check_plugin_redfish_memory_summary = CheckPlugin(
    name="redfish_memory_summary",
    service_name="Memory %s",
    sections=["redfish_system"],
    discovery_function=discover_redfish_memory_summary,
    check_function=check_redfish_memory_summary,
)

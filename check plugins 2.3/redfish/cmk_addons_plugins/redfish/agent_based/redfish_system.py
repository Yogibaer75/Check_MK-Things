#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# (c) Andre Eckstein <andre.eckstein@bechtle.com>

# License: GNU General Public License v2
import json
from typing import Any, Dict, Mapping

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    StringTable,
)
from cmk_addons.plugins.redfish.lib import (
    RedfishAPIData,
    redfish_health_state,
)

Section = Dict[str, Mapping[str, Any]]


def parse_redfish_system(string_table: StringTable) -> Section | None:
    if not string_table:
        return None

    raw = json.loads(string_table[0][0])
    return {
        str(entry.get("Id", "0")): {str(k): v for k, v in entry.items()}
        for entry in raw
    }


agent_section_redfish_system = AgentSection(
    name="redfish_system",
    parse_function=parse_redfish_system,
    parsed_section_name="redfish_system",
)


def discover_redfish_system(section: RedfishAPIData) -> DiscoveryResult:
    yield from (Service(item=item) for item in section)


def check_redfish_system(item: str, section: RedfishAPIData) -> CheckResult:
    if not (data := section.get(item)):
        return

    if serial := data.get("SerialNumber"):
        yield Result(state=State(0), summary=f"Serial Number: {serial}")

    details = []
    if sku_data := data.get("SKU"):
        details.append(f"SKU: {sku_data}")

    if dell_data := (data.get("Oem") or {}).get("Dell", {}).get("DellSystem", {}):
        for key in dell_data.keys():
            if "Rollup" in key or "Tag" in key or "Code" in key:
                key_name = (
                    key.replace("Rollup", " Rollup")
                    .replace("Status", " Status")
                    .strip()
                )
                details.append(f"{key_name}: {dell_data[key]}")

    if details:
        details_msg = "\n".join(details)
    else:
        details_msg = "No additional details available."

    dev_state, dev_msg = redfish_health_state(data.get("Status", {}))
    yield Result(state=State(dev_state), summary=dev_msg, details=details_msg)


check_plugin_redfish_system = CheckPlugin(
    name="redfish_system",
    service_name="System %s",
    sections=["redfish_system"],
    discovery_function=discover_redfish_system,
    check_function=check_redfish_system,
)

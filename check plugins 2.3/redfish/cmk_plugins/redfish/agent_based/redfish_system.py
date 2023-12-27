#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# (c) Andre Eckstein <andre.eckstein@bechtle.com>

# License: GNU General Public License v2

from typing import Any, Dict, Mapping
from cmk.agent_based.v2 import AgentSection, CheckPlugin, Result, Service, State
from cmk.agent_based.v2.type_defs import CheckResult, DiscoveryResult
from cmk.plugins.redfish.lib import RedfishAPIData, parse_redfish, redfish_health_state

Section = Dict[str, Mapping[str, Any]]


agent_section_apt = AgentSection(
    name="redfish_system",
    parse_function=parse_redfish,
    parsed_section_name="redfish_system",
)


def discover_redfish_system(section: RedfishAPIData) -> DiscoveryResult:
    if section:
        yield Service()


def check_redfish_system(section: RedfishAPIData) -> CheckResult:
    if not section:
        return

    for entry in section:
        state = entry.get("Status", {"Health": "Unknown"})
        result_state, state_text = redfish_health_state(state)
        message = f"System with SerialNr: {entry.get('SerialNumber')}, has State: {state_text}"

        yield Result(state=State(result_state), summary=message)


check_plugin_redfish_system = CheckPlugin(
    name="redfish_system",
    service_name="System state",
    sections=["redfish_system"],
    discovery_function=discover_redfish_system,
    check_function=check_redfish_system,
)

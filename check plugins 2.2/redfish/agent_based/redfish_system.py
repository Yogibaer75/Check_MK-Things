#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from typing import Any, Dict, Mapping
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
    Result,
    State,
    Service,
)

from .utils.redfish import RedfishAPIData, parse_redfish, redfish_health_state

Section = Dict[str, Mapping[str, Any]]


register.agent_section(
    name="redfish_system",
    parse_function=parse_redfish,
)


def discover_redfish_system(section: RedfishAPIData) -> DiscoveryResult:
    if not section:
        return
    if len(section) == 1:
        yield Service(item="state")
    else:
        for element in section:
            item = f"state {element.get('Id', '0')}"
            yield Service(item=item)


def check_redfish_system(item: str, section: RedfishAPIData) -> CheckResult:
    if not section:
        return
    data = None
    if len(section) == 1:
        data = section[0]
    else:
        for element in section:
            if f"state {element.get('Id')}" == item:
                data = element
                break

    if not data:
        return

    state = data.get("Status", {"Health": "Unknown"})
    result_state, state_text = redfish_health_state(state)
    message = f"System with SerialNr: {data.get('SerialNumber')}, has State: {state_text}"

    yield Result(state=State(result_state), summary=message)


register.check_plugin(
    name="redfish_system",
    service_name="System %s",
    sections=["redfish_system"],
    discovery_function=discover_redfish_system,
    check_function=check_redfish_system,
)

#!/usr/bin/env python3
"""check single redfish outlet state"""
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from collections.abc import Mapping
from typing import Any
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Result,
    Service,
    State,
    register,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)
from cmk.base.plugins.agent_based.utils.elphase import (
    check_elphase,
)
from .utils.redfish import (
    RedfishAPIData,
    parse_redfish_multiple,
    redfish_health_state,
)


register.agent_section(
    name="redfish_outlets",
    parse_function=parse_redfish_multiple,
    parsed_section_name="redfish_outlets",
)


def discovery_redfish_outlets(section: RedfishAPIData) -> DiscoveryResult:
    """Discover single sensors"""
    for key in section.keys():
        if section[key].get("Status", {}).get("State") == "Absent":
            continue
        yield Service(item=section[key]["Id"])


def check_redfish_outlets(
    item: str, params: Mapping[str, Any], section: RedfishAPIData
) -> CheckResult:
    """Check single outlet state"""
    data = section.get(item, None)
    if data is None:
        return

    socket_data = {
        item: {
            "voltage": data.get("Voltage", {}).get("Reading"),
            "current": data.get("CurrentAmps", {}).get("Reading"),
            "power": data.get("PowerWatts", {}).get("Reading"),
            "frequency": data.get("FrequencyHz", {}).get("Reading"),
        }
    }

    if all(value is not None for value in socket_data[item].values()):
        yield from check_elphase(item, params, socket_data)

    dev_state, dev_msg = redfish_health_state(data.get("Status", {}))
    yield Result(state=State(dev_state), notice=dev_msg)


register.check_plugin(
    name="redfish_outlets",
    service_name="Outlet %s",
    sections=["redfish_outlets"],
    discovery_function=discovery_redfish_outlets,
    check_function=check_redfish_outlets,
    check_default_parameters={},
    check_ruleset_name="ups_outphase",
)

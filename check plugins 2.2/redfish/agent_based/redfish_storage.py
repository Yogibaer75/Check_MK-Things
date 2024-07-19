#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

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

from .utils.redfish import parse_redfish_multiple, redfish_health_state

register.agent_section(
    name="redfish_storage",
    parse_function=parse_redfish_multiple,
)


def discovery_redfish_storage(section) -> DiscoveryResult:
    """Discover single controllers"""
    for key in section.keys():
        if section[key].get("Status", {}).get("State") == "UnavailableOffline":
            continue
        yield Service(item=section[key]["Id"])


def check_redfish_storage(item: str, section) -> CheckResult:
    """Check single Controller state"""
    data = section.get(item, None)
    if data is None:
        return

    controller_list = data.get("StorageControllers", [])
    if len(controller_list) == 1:
        for ctrl_data in controller_list:
            storage_msg = (
                f"Type: {ctrl_data.get('Model')}, "
                f"RaidLevels: {','.join(ctrl_data.get('SupportedRAIDTypes', []))}, "
                f"DeviceProtocols: {','.join(ctrl_data.get('SupportedDeviceProtocols', []))}"
            )
            dev_state, dev_msg = redfish_health_state(ctrl_data.get("Status", {}))
            yield Result(state=State(dev_state), summary=storage_msg, details=dev_msg)
    elif len(controller_list) > 1:
        global_state = 0
        global_msg = ""
        for ctrl_data in controller_list:
            storage_msg = (
                f"Type: {ctrl_data.get('Model')}, "
                f"RaidLevels: {','.join(ctrl_data.get('SupportedRAIDTypes', []))}, "
                f"DeviceProtocols: {','.join(ctrl_data.get('SupportedDeviceProtocols', []))}"
            )
            dev_state, dev_msg = redfish_health_state(ctrl_data.get("Status", {}))
            global_state = max(global_state, dev_state)
            yield Result(state=State(dev_state), details=storage_msg, notice=dev_msg)
        if global_state != 0:
            global_msg = "One or more controllers with problems"
        else:
            global_msg = "All controllers are working properly"
        yield Result(state=State(global_state), summary=global_msg)
    else:
        dev_state, dev_msg = redfish_health_state(data.get("Status", {}))
        yield Result(state=State(dev_state), notice=dev_msg)


register.check_plugin(
    name="redfish_storage",
    service_name="Storage controller %s",
    sections=["redfish_storage"],
    discovery_function=discovery_redfish_storage,
    check_function=check_redfish_storage,
)

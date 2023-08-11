#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

# Example Output:
#
#
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

from .utils.redfish import parse_redfish_multiple, redfish_health_state

register.agent_section(
    name="redfish_storage",
    parse_function=parse_redfish_multiple,
)


def discovery_redfish_storage(section) -> DiscoveryResult:
    """Discover single controllers"""
    for key in section.keys():
        yield Service(item=section[key]["Id"])


def check_redfish_storage(item: str, section) -> CheckResult:
    """Check single Controller state"""
    data = section.get(item, None)
    if data is None:
        return

    controller_list = data.get("StorageControllers", [])
    if len(controller_list) == 1:
        for ctrl_data in controller_list:
            storage_msg = f"Type: {ctrl_data.get('Model')}, \
                RaidLevels: {','.join(ctrl_data.get('SupportedRAIDTypes', []))}, \
                DeviceProtocols: {','.join(ctrl_data.get('SupportedDeviceProtocols', []))}"
            dev_state, dev_msg = redfish_health_state(ctrl_data.get("Status", {}))
            yield Result(state=State(dev_state), summary=storage_msg, details=dev_msg)
    elif len(controller_list) > 1:
        global_state = 0
        global_msg = ""
        for ctrl_data in controller_list:
            storage_msg = f"Type: {ctrl_data.get('Model')}, \
                RaidLevels: {','.join(ctrl_data.get('SupportedRAIDTypes', []))}, \
                DeviceProtocols: {','.join(ctrl_data.get('SupportedDeviceProtocols', []))}\n"
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
    service_name="Storage Controller %s",
    sections=["redfish_storage"],
    discovery_function=discovery_redfish_storage,
    check_function=check_redfish_storage,
)

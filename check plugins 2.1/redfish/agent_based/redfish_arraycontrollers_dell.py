#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# This is free software;  you can redistribute it and/or modifdell_redfishy it
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

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)

from .agent_based_api.v1 import register, Result, State, Service
from .utils.redfish import redfish_health_state


def discovery_redfish_arraycontrollers_dell(section) -> DiscoveryResult:
    for key in section.keys():
        if section[key].get("Oem"):
            if section[key]["Oem"].get("Dell"):
                yield Service(item=section[key]["Id"])


def check_redfish_arraycontrollers_dell(item: str, section) -> CheckResult:
    data = section.get(item, None)
    if data is None:
        return

    if data.get("StorageControllers@odata.count") == 1:
        ctrl_data = data.get("StorageControllers")[0]

        storage_msg = "Type: %s, RaidLevels: %s, DeviceProtocols: %s" % (
            ctrl_data.get("Model"),
            ",".join(ctrl_data.get("SupportedRAIDTypes", [])),
            ",".join(ctrl_data.get("SupportedDeviceProtocols", [])),
        )
        yield Result(state=State(0), summary=storage_msg)

    dev_state, dev_msg = redfish_health_state(data["Status"])
    status = dev_state
    message = dev_msg

    yield Result(state=State(status), notice=message)


register.check_plugin(
    name="redfish_arraycontrollers_dell",
    service_name="Storage Controller %s",
    sections=["redfish_arraycontrollers"],
    discovery_function=discovery_redfish_arraycontrollers_dell,
    check_function=check_redfish_arraycontrollers_dell,
)

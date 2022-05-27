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
from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)

from .agent_based_api.v1 import register, Result, State, Service

from .utils.redfish import parse_redfish_multiple, redfish_health_state

register.agent_section(
    name="redfish_memory",
    parse_function=parse_redfish_multiple,
)

LEGACY_DIMM_STATE = {
    "Unknown": 3,
    "Other": 1,
    "NotPresent": 1,
    "PresentUnused": 0,
    "GoodInUse": 0,
    "AddedButUnused": 0,
    "UpgradedButUnused": 0,
    "ExpectedButMissing": 1,
    "DoesNotMatch": 1,
    "NotSupported": 1,
    "ConfigurationError": 2,
    "Degraded": 1,
    "PresentSpare": 0,
    "GoodPartiallyInUse": 0,
}


def discovery_redfish_memory(section) -> DiscoveryResult:
    for key in section.keys():
        if section[key].get("Status"):
            if section[key].get("Status").get("State") == "Absent":
                continue
        yield Service(item=section[key]["Id"])


def check_redfish_memory(item: str, section) -> CheckResult:
    data = section.get(item, None)
    if data is None:
        return

    capacity = data.get("CapacityMiB")
    if not capacity:
        capacity = data.get("SizeMB", 0)
    memtype = data.get("MemoryDeviceType")
    if not memtype:
        memtype = data.get("DIMMType")
    opspeed = data.get("OperatingSpeedMhz")
    if not opspeed:
        opspeed = data.get("MaximumFrequencyMHz")
    errcor = data.get("ErrorCorrection")

    mem_msg = "Size: %0.0fGB, Type: %s-%s %s" % (
        capacity / 1024,
        memtype,
        opspeed,
        errcor,
    )
    yield Result(state=State(0), summary=mem_msg)

    if data.get("Status"):
        dev_state, dev_msg = redfish_health_state(data["Status"])
        status = dev_state
        message = dev_msg
    elif data.get("DIMMStatus"):
        status = 0
        message = data.get("DIMMStatus")
    else:
        status = 0
        message = "No known status value found"

    yield Result(state=State(status), notice=message)


register.check_plugin(
    name="redfish_memory",
    service_name="Memory Module %s",
    sections=["redfish_memory"],
    discovery_function=discovery_redfish_memory,
    check_function=check_redfish_memory,
)

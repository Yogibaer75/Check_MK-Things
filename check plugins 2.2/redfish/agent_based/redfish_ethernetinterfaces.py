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
    name="redfish_ethernetinterfaces",
    parse_function=parse_redfish_multiple,
)


def discovery_redfish_ethernetinterfaces(section) -> DiscoveryResult:
    for key in section.keys():
        if not section[key].get("Status"):
            continue
        if section[key].get("Status", {}).get("State") in [
            "Absent",
            "Disabled",
            "Offline",
            "UnavailableOffline",
        ]:
            continue
        yield Service(item=section[key]["Id"])


def check_redfish_ethernetinterfaces(item: str, section) -> CheckResult:
    data = section.get(item, None)
    if data is None:
        return

    mac_addr = ""
    if data.get("AssociatedNetworkAddresses"):
        mac_addr = ", ".join(data.get("AssociatedNetworkAddresses"))
    elif data.get("MACAddress"):
        mac_addr = data.get("MACAddress")

    link_speed = 0
    if data.get("CurrentLinkSpeedMbps"):
        link_speed = data.get("CurrentLinkSpeedMbps")
    elif data.get("SpeedMbps"):
        link_speed = data.get("SpeedMbps")
    if link_speed is None:
        link_speed = 0

    link_status = "Unknown"
    if data.get("LinkStatus"):
        link_status = data.get("LinkStatus")
        if link_status is None:
            link_status = "Down"

    int_msg = "Link: %s, Speed: %0.0fMbps, MAC: %s" % (
        link_status,
        link_speed,
        mac_addr,
    )
    yield Result(state=State(0), summary=int_msg)

    if data.get("Status"):
        dev_state, dev_msg = redfish_health_state(data["Status"])
        status = dev_state
        message = dev_msg
    else:
        status = 0
        message = "No known status value found"

    yield Result(state=State(status), notice=message)


register.check_plugin(
    name="redfish_ethernetinterfaces",
    service_name="Network Interface %s",
    sections=["redfish_ethernetinterfaces"],
    discovery_function=discovery_redfish_ethernetinterfaces,
    check_function=check_redfish_ethernetinterfaces,
)

#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

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
from .utils.redfish import (
    RedfishAPIData,
    parse_redfish_multiple,
    redfish_health_state,
)

register.agent_section(
    name="redfish_ethernetinterfaces",
    parse_function=parse_redfish_multiple,
)


def discovery_redfish_ethernetinterfaces(section: RedfishAPIData) -> DiscoveryResult:
    for key in section.keys():
        if not section[key].get("Status"):
            continue
        if section[key].get("Status", {}).get("State") in ["Absent", "Disabled"]:
            continue
        yield Service(item=section[key]["Id"])


def check_redfish_ethernetinterfaces(item: str, section: RedfishAPIData) -> CheckResult:
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

    int_msg = f"Link: {link_status}, Speed: {link_speed:0.0f}Mbps, MAC: {mac_addr}"
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
    service_name="Physical port %s",
    sections=["redfish_ethernetinterfaces"],
    discovery_function=discovery_redfish_ethernetinterfaces,
    check_function=check_redfish_ethernetinterfaces,
)

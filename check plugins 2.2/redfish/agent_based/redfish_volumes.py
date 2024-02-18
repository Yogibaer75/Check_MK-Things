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
    name="redfish_volumes",
    parse_function=parse_redfish_multiple,
)


def discovery_redfish_volumes(section) -> DiscoveryResult:
    for key in section.keys():
        yield Service(item=section[key]["Id"])


def check_redfish_volumes(item: str, section) -> CheckResult:
    data = section.get(item, None)
    if data is None:
        return
    volume_msg = "Raid Type: %s, Size: %0.1fGB" % (
        data.get("RAIDType", None),
        int(data.get("CapacityBytes", 0.0)) / 1024 / 1024 / 1024,
    )
    yield Result(state=State(0), summary=volume_msg)

    dev_state, dev_msg = redfish_health_state(data["Status"])
    status = dev_state
    message = dev_msg

    yield Result(state=State(status), notice=message)


register.check_plugin(
    name="redfish_volumes",
    service_name="Volume %s",
    sections=["redfish_volumes"],
    discovery_function=discovery_redfish_volumes,
    check_function=check_redfish_volumes,
)

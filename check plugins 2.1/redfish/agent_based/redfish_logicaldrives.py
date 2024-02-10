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
    redfish_item_hpe,
)

register.agent_section(
    name="redfish_logicaldrives",
    parse_function=parse_redfish_multiple,
)


def discovery_redfish_logicaldrives(section: RedfishAPIData) -> DiscoveryResult:
    for key in section.keys():
        if "SmartStorageLogicalDrive" in section[key].get("@odata.type"):
            item = redfish_item_hpe(section[key])
        else:
            item = section[key]["Id"]
        yield Service(item=item)


def check_redfish_logicaldrives(item: str, section: RedfishAPIData) -> CheckResult:
    data = section.get(item, None)
    if data is None:
        return

    raid_type = data.get("RAIDType", None)
    if not raid_type:
        raid_type = "RAID%s" % data.get("Raid", " Unknown")

    size = data.get("CapacityBytes")
    if not size:
        size = data.get("CapacityMiB") / 1024
    else:
        size = size / 1024 / 1024 / 1024

    volume_msg = "Raid Type: %s, Size: %0.0fGB" % (raid_type, size)
    yield Result(state=State(0), summary=volume_msg)

    dev_state, dev_msg = redfish_health_state(data["Status"])
    status = dev_state
    message = dev_msg

    yield Result(state=State(status), notice=message)


register.check_plugin(
    name="redfish_logicaldrives",
    service_name="Volume %s",
    sections=["redfish_logicaldrives"],
    discovery_function=discovery_redfish_logicaldrives,
    check_function=check_redfish_logicaldrives,
)

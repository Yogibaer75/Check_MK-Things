#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
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
    name="redfish_physicaldrives",
    parse_function=parse_redfish_multiple,
)


def discovery_redfish_physicaldrives(section) -> DiscoveryResult:
    for key in section.keys():
        loc = section[key].get("Location")
        if loc == []:
            item = section[key]["Name"]
        else:
            item = section[key]["Location"]

        yield Service(item=item)


def check_redfish_physicaldrives(item: str, section) -> CheckResult:
    data = None
    for key in section.keys():
        if item == section[key].get("Location"):
            data = section.get(key, None)
        elif item == section[key].get("Name"):
            data = section.get(key, None)
    if data is None:
        return

    capacity = data.get("CapacityBytes", None)
    if not capacity:
        capacity = data.get("CapacityMiB", None)
        if capacity:
            capacity = capacity / 1024
    else:
        capacity = capacity / 1024 / 1024 / 1024

    speed = data.get("CapableSpeedGbs", None)
    if not speed:
        speed = data.get("InterfaceSpeedMbps", 0)
        speed = speed / 1000

    disc_msg = "Size: %0.0fGB, Speed %s Gbs" % (
        capacity,
        speed,
    )

    if data.get("MediaType") == "SSD":
        if data.get("PredictedMediaLifeLeftPercent"):
            disc_msg = disc_msg + ", Media Life Left: %d%%" % (
                int(data.get("PredictedMediaLifeLeftPercent", 0))
            )
        elif data.get("SSDEnduranceUtilizationPercentage"):
            disc_msg = disc_msg + ", SSD Utilization: %d%%" % (
                int(data.get("SSDEnduranceUtilizationPercentage", 0))
            )
    yield Result(state=State(0), summary=disc_msg)

    dev_state, dev_msg = redfish_health_state(data["Status"])
    status = dev_state
    message = dev_msg
    yield Result(state=State(status), notice=message)

    dev_ser = data.get("SerialNumber")
    dev_mod = data.get("Model")
    yield Result(state=State(0), notice="Serial: %s\nModel: %s" % (dev_ser, dev_mod))

    if data.get("CurrentTemperatureCelsius", None):
        yield Metric("temp", int(data.get("CurrentTemperatureCelsius")))


register.check_plugin(
    name="redfish_physicaldrives",
    service_name="Drive %s",
    sections=["redfish_physicaldrives"],
    discovery_function=discovery_redfish_physicaldrives,
    check_function=check_redfish_physicaldrives,
)

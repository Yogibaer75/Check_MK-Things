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
    Metric,
)
from .utils.redfish import (
    RedfishAPIData,
    redfish_health_state,
)


def discovery_redfish_psu(section: RedfishAPIData) -> DiscoveryResult:
    for key in section.keys():
        data = section[key].get("PowerSupplies", None)
        if data:
            for count, entry in enumerate(data):
                if entry.get("Status", {}).get("State") in ["Absent", "Disabled"]:
                    continue
                yield Service(item=f"{count}-{entry['Name']}")


def check_redfish_psu(item: str, section: RedfishAPIData) -> CheckResult:
    psu = None
    for key in section.keys():
        psus = section[key].get("PowerSupplies", None)
        if psus is None:
            return

        for count, psu_data in enumerate(psus):
            if f"{count}-{psu_data.get('Name')}" == item:
                psu = psu_data
                break
        if psu:
            break

    if psus is None:
        return

    output_power = float(
        0
        if psu.get("PowerOutputWatts", psu.get("LastPowerOutputWatts")) is None
        else psu.get("PowerOutputWatts", psu.get("LastPowerOutputWatts"))
    )
    input_power = float(
        0 if psu.get("PowerInputWatts") is None else psu.get("PowerInputWatts")
    )
    input_voltage = float(
        0
        if psu.get("LineInputVoltage") is None
        else psu.get("LineInputVoltage")
    )
    dev_model = psu.get("Model")
    capacity = float(
        0
        if psu.get("PowerCapacityWatts") is None
        else psu.get("PowerCapacityWatts")
    )

    yield Metric("input_power", input_power)
    yield Metric("output_power", output_power)
    yield Metric("input_voltage", input_voltage)

    model_msg = (f"{input_power} Watts input, {output_power} Watts output, "
                 f"{input_voltage} V input, Capacity {capacity} Watts, Typ {dev_model}")
    yield Result(state=State(0), summary=model_msg)
    dev_state, dev_msg = redfish_health_state(psu["Status"])
    yield Result(state=State(dev_state), notice=dev_msg)


register.check_plugin(
    name="redfish_psu",
    service_name="PSU %s",
    sections=["redfish_power"],
    discovery_function=discovery_redfish_psu,
    check_function=check_redfish_psu,
)

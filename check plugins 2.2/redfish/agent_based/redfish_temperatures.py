#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
'''Redfish temperature checks'''
# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Result,
    Service,
    State,
    get_value_store,
    register,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)
from cmk.base.plugins.agent_based.utils.temperature import (
    TempParamDict,
    check_temperature,
)

from .utils.redfish import process_redfish_perfdata, redfish_health_state


def discovery_redfish_temperatures(section) -> DiscoveryResult:
    """Discover temperature sensors"""
    for key in section.keys():
        temps = section[key].get("Temperatures", None)
        if not temps:
            continue
        for temp in temps:
            if temp.get("Status").get("State") in ["Absent", "Disabled"]:
                continue
            if not temp.get("ReadingCelsius"):
                continue
            if temp.get("Name"):
                yield Service(item=temp.get("Name"))


def check_redfish_temperatures(
    item: str, params: TempParamDict, section
) -> CheckResult:
    """Check single temperature sensor state"""
    temp = None
    for key in section.keys():
        temps = section[key].get("Temperatures", None)
        if temps is None:
            return

        for temp_data in temps:
            if temp_data.get("Name") == item:
                temp = temp_data
                break
        if temp:
            break

    if not temp:
        return

    perfdata = process_redfish_perfdata(temp)
    if perfdata:
        yield from check_temperature(
            perfdata.value,
            params,
            unique_name=f"redfish.temp.{item}",
            value_store=get_value_store(),
            dev_levels=perfdata.levels_upper,
            dev_levels_lower=perfdata.levels_lower,
        )
    else:
        yield Result(state=State(0), summary="No temperature data found")

    dev_state, dev_msg = redfish_health_state(temp["Status"])
    yield Result(state=State(dev_state), notice=dev_msg)


register.check_plugin(
    name="redfish_temperatures",
    service_name="Temperature %s",
    sections=["redfish_thermal"],
    discovery_function=discovery_redfish_temperatures,
    check_function=check_redfish_temperatures,
    check_default_parameters={},
    check_ruleset_name="temperature",
)

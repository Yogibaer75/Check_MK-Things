#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    State,
)
from cmk_addons.plugins.redfish.lib import (
    RedfishAPIData,
)


def discovery_redfish_power_consumption(section: RedfishAPIData) -> DiscoveryResult:
    for key in section.keys():
        if section[key].get("PowerControl", None):
            yield Service()


def check_redfish_power_consumption(section: RedfishAPIData) -> CheckResult:
    powercontrol = []
    for key in section.keys():
        if powercontrol_element := section[key].get("PowerControl", None):
            powercontrol.extend(powercontrol_element)

    if not powercontrol:
        return
    result_submited = False
    for element in powercontrol:
        summary_msg = []
        mem_id = element.get("MemberId", "0")
        mem_name = element.get("Name", "PowerControl")
        system_wide_values = {}
        for i in ["PowerCapacityWatts", "PowerConsumedWatts"]:
            if (value := element.get(i, None)) is not None:
                system_wide_values[i] = value
                summary_msg.append(f"{i} - {value} W")

        if summary_msg:
            result_submited = True
            yield Result(
                state=State(0), summary=f"{mem_name}: {' / '.join(summary_msg)}"
            )
        if metrics := element.get("PowerMetrics", None):
            for metric_name in [
                "AverageConsumedWatts",
                "MinConsumedWatts",
                "MaxConsumedWatts",
            ]:
                if (metric_value := metrics.get(metric_name, None)) is not None:
                    maximum_value = system_wide_values.get("PowerCapacityWatts", None)
                    if maximum_value:
                        yield Metric(
                            name=f"{metric_name.lower()}_{mem_id}",
                            value=float(metric_value),
                            boundaries=(0, float(maximum_value)),
                        )
                    else:
                        yield Metric(
                            name=f"{metric_name.lower()}_{mem_id}",
                            value=float(metric_value),
                        )
    if not result_submited:
        yield Result(
            state=State(0),
            summary="No power consumption data available.",
        )


check_plugin_redfish_power_consumption = CheckPlugin(
    name="redfish_power_consumption",
    service_name="Power consumption",
    sections=["redfish_power"],
    discovery_function=discovery_redfish_power_consumption,
    check_function=check_redfish_power_consumption,
)

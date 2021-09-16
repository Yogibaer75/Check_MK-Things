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

# <<<ilo_api_power_metrics:sep(124)
# 0|0|3200|282
# PowerAllocatedWatts | PowerAvailableWatts | PowerCapacityWatts | PowerConsumedWatts

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)

from .agent_based_api.v1 import (
    register,
    Result,
    State,
    Service,
    Metric,
)


def parse_hp_ilo_metric(string_table):
    parsed = {}
    parsed["Metric"] = string_table[0]
    return parsed


register.agent_section(
    name="ilo_api_power_metrics",
    parse_function=parse_hp_ilo_metric,
)


def discovery_ilo_api_power_metrics(section) -> DiscoveryResult:
    for element in section:
        yield Service(item=element)


def check_ilo_api_power_metrics(item: str, section) -> CheckResult:
    data = section.get(item)
    if data:
        yield Result(state=State(0),
                     summary="Overall power consumption %d Watts from available %d Watts" % (int(data[3]), int(data[2])))
        yield Metric("watt", int(data[3]), boundaries=(0, int(data[2])))


register.check_plugin(
    name="ilo_api_power_metrics",
    service_name="HW PSU %s",
    sections=["ilo_api_power_metrics"],
    discovery_function=discovery_ilo_api_power_metrics,
    check_function=check_ilo_api_power_metrics,
)

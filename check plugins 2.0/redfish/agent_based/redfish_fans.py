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
    CheckResult, DiscoveryResult,)

from .agent_based_api.v1 import (register, Result, State, Service, check_levels)

from .utils.redfish import (process_redfish_perfdata, redfish_health_state)


def discovery_redfish_fans(section) -> DiscoveryResult:
    fans = section.get("Fans", None)
    for fan in fans:
        if fan.get("Status").get("State") == "Absent":
            continue
        if fan.get("Name"):
            yield Service(item=fan.get("Name"))
        elif fan.get("FanName"):
            yield Service(item=fan.get("FanName"))


def check_redfish_fans(item: str, section) -> CheckResult:
    fans = section.get("Fans", None)
    if fans is None:
        return

    for fan in fans:
        if (fan.get("Name") or fan.get("FanName")) == item:
            perfdata = process_redfish_perfdata(fan)
            units = fan.get("ReadingUnits")
            if units == "Percent":
                yield from check_levels(
                    perfdata.value,
                    levels_upper=perfdata.levels_upper,
                    levels_lower=perfdata.levels_lower,
                    metric_name="perc",
                    label="Speed",
                    render_func=lambda v: "%.1f%%" % v,
                    boundaries=(0, 100)
                )
            elif units == "RPM":
                yield from check_levels(
                    perfdata.value,
                    levels_upper=perfdata.levels_upper,
                    levels_lower=perfdata.levels_lower,
                    metric_name="fan",
                    label="Speed",
                    render_func=lambda v: "%.1f rpm" % v,
                    boundaries=perfdata.boundaries
                )
            else:
                yield Result(state=State(0), summary="No performance data available")

            dev_state, dev_msg = redfish_health_state(fan["Status"])

            yield Result(state=State(dev_state), notice=dev_msg)


register.check_plugin(
    name="redfish_fans",
    service_name="%s",
    sections=["redfish_thermal"],
    discovery_function=discovery_redfish_fans,
    check_function=check_redfish_fans,
)

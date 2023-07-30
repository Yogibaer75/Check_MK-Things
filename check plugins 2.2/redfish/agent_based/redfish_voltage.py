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
    check_levels,
)

from .utils.redfish import redfish_health_state, process_redfish_perfdata


def discovery_redfish_voltage(section) -> DiscoveryResult:
    data = section.get("Voltages", None)
    if not data:
        return
    for entry in data:
        if not entry.get("ReadingVolts"):
            continue
        yield Service(item=entry["Name"])


def check_redfish_voltage(item: str, section) -> CheckResult:
    voltages = section.get("Voltages", None)
    if voltages is None:
        return

    for voltage in voltages:
        if voltage.get("Name") == item:
            perfdata = process_redfish_perfdata(voltage)

            volt_msg = "Location: %s, SensorNr: %s" % (
                voltage.get("PhysicalContext"),
                voltage.get("SensorNumber"),
            )
            yield Result(state=State(0), summary=volt_msg)

            if perfdata.value is not None:
                yield from check_levels(
                    perfdata.value,
                    levels_upper=perfdata.levels_upper,
                    levels_lower=perfdata.levels_lower,
                    metric_name="voltage",
                    label="Value",
                    render_func=lambda v: "%.1f V" % v,
                    boundaries=perfdata.boundaries,
                )

            dev_state, dev_msg = redfish_health_state(voltage["Status"])
            yield Result(state=State(dev_state), notice=dev_msg)


register.check_plugin(
    name="redfish_voltage",
    service_name="Voltage %s",
    sections=["redfish_power"],
    discovery_function=discovery_redfish_voltage,
    check_function=check_redfish_voltage,
)

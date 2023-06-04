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
    Metric,
)

from .dell_powervault_me4 import (parse_dell_powervault_me4)

register.agent_section(
    name="dell_powervault_me4_sensor_status",
    parse_function=parse_dell_powervault_me4,
)


def discovery_dell_powervault_me4_sensor_status(section) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_dell_powervault_me4_sensor_status(item: str, params,
                                            section) -> CheckResult:
    data = section.get(item)
    sensor_states = {
        0: ("Unsupported", 3),
        1: ("OK", 0),
        2: ("Critical", 2),
        3: ("Warning", 1),
        4: ("Unrecoverable", 2),
        5: ("Not Installed", 1),
        6: ("Unknown", 3),
        7: ("Unavailable", 3),
    }

    sensor_unit = {
        "Temperature": ("°C", "temp"),
        "Voltage": ("V", "voltage"),
        "Charge Capacity": ("%", "battery_capacity"),
        "Current": ("A", "current"),
        "Unknown": ("", ""),
    }
    value = data.get("value")
    value_number = ''.join(c for c in value if (c.isdigit() or c == "."))
    status_unit, perf_unit = sensor_unit.get(
        data.get("sensor-type", "Unknown"), ("", "count"))
    state_text, status_num = sensor_states.get(data.get("status-numeric", 7),
                                               ("Unknown", 3))
    message = "Sensor state is %s" % (state_text)
    if value_number != "":
        message += " with reading %s%s" % (value_number, status_unit)
    yield Result(state=State(status_num), summary=message)

    if status_unit != "":
        yield Metric(perf_unit, float(value_number))


register.check_plugin(
    name="dell_powervault_me4_sensor_status",
    service_name="Sensor %s",
    sections=["dell_powervault_me4_sensor_status"],
    check_default_parameters={
        'sensor_state': 0,
    },
    discovery_function=discovery_dell_powervault_me4_sensor_status,
    check_function=check_dell_powervault_me4_sensor_status,
    check_ruleset_name="dell_powervault_me4_sensor_status",
)

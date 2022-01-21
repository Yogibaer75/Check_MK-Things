#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# (c) Andre Eckstein <andre.eckstein@bechtle.com>

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
    CheckResult, )

from .agent_based_api.v1 import (register, Result, State, Metric)

from .utils.lenovo_xclarity import (parse_lenovo_xclarity,
                                    discovery_lenovo_xclarity_multiple)

register.agent_section(
    name="lenovo_xclarity_power_supply",
    parse_function=parse_lenovo_xclarity,
)


def check_lenovo_xclarity_power_supply(item: str, section) -> CheckResult:
    data = section.get(item)
    state = data.get("Status", {"Health": "Unknown"}).get("Health", "Unknown")
    reading = data.get("PowerInputWatts", 0)
    reading_output = data.get("PowerOutputWatts", 0)

    reading = float(0 if reading is None else reading)
    reading_output = float(0 if reading_output is None else reading_output)

    message = "reading is %s Watt input, %s Watt output and has status %s" % (
        reading,
        reading_output,
        state,
    )
    status = 0
    if state != "OK":
        message += "(!)"
        status = 1

    yield Metric("input_power", reading)
    yield Metric("output_power", reading_output)
    yield Result(state=State(status), summary=message)


register.check_plugin(
    name="lenovo_xclarity_power_supply",
    service_name="%s",
    sections=["lenovo_xclarity_power_supply"],
    discovery_function=discovery_lenovo_xclarity_multiple,
    check_function=check_lenovo_xclarity_power_supply,
)

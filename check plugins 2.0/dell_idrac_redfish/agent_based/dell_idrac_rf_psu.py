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
    CheckResult,
    DiscoveryResult,
)

from .agent_based_api.v1 import (register, Result, State, Service, Metric)

from .utils.dell_idrac import (idrac_health_state)


def discovery_dell_idrac_rf_psu(section) -> DiscoveryResult:
    data = section.get("PowerSupplies", None)
    for entry in data:
        yield Service(item=entry["Name"])


def check_dell_idrac_rf_psu(item: str, section) -> CheckResult:
    psus = section.get("PowerSupplies", None)
    if psus is None:
        return

    for psu in psus:
        if psu.get("Name") == item:

            output_power = float(0 if psu.get("PowerOutputWatts") is None else
                                 psu.get("PowerOutputWatts"))
            input_power = float(0 if psu.get("PowerInputWatts") is None else
                                psu.get("PowerInputWatts"))
            input_voltage = float(0 if psu.get("LineInputVoltage") is None else
                                  psu.get("LineInputVoltage"))
            dev_model = psu.get("Model")
            capacity = float(0 if psu.get("PowerCapacityWatts") is None else
                             psu.get("PowerCapacityWatts"))

            yield Metric("input_power", input_power)
            yield Metric("output_power", output_power)
            yield Metric("input_voltage", input_voltage)

            model_msg = "%s Watts input, %s Watts output, %s V input, Capacity %s Watts, Typ %s" % (
                input_power,
                output_power,
                input_voltage,
                capacity,
                dev_model,
            )
            yield Result(state=State(0), summary=model_msg)
            dev_state, dev_msg = idrac_health_state(psu["Status"])
            yield Result(state=State(dev_state), summary=dev_msg)


register.check_plugin(
    name="dell_idrac_rf_psu",
    service_name="PSU %s",
    sections=["dell_idrac_rf_power"],
    discovery_function=discovery_dell_idrac_rf_psu,
    check_function=check_dell_idrac_rf_psu,
)

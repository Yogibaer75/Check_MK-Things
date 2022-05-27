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

from .agent_based_api.v1 import register, Result, State, Service, get_value_store
from .utils.temperature import check_temperature, TempParamDict
from .utils.redfish import process_redfish_perfdata, redfish_health_state


def discovery_redfish_temperatures(section) -> DiscoveryResult:
    temps = section.get("Temperatures", None)
    for temp in temps:
        if temp.get("Status").get("State") == "Absent":
            continue
        if temp.get("Name"):
            yield Service(item=temp.get("Name"))


def check_redfish_temperatures(
    item: str, params: TempParamDict, section
) -> CheckResult:
    temps = section.get("Temperatures", None)
    if temps is None:
        return

    for temp in temps:
        if temp.get("Name") == item:
            dev_state, dev_msg = redfish_health_state(temp["Status"])
            if dev_state == 0:
                perfdata = process_redfish_perfdata(temp)

                yield from check_temperature(
                    perfdata.value,
                    params,
                    unique_name="redfish.temp.%s" % item,
                    value_store=get_value_store(),
                    dev_levels=perfdata.levels_upper,
                    dev_levels_lower=perfdata.levels_lower,
                )

            yield Result(state=State(dev_state), notice=dev_msg)


register.check_plugin(
    name="redfish_temperatures",
    service_name="Temp %s",
    sections=["redfish_thermal"],
    discovery_function=discovery_redfish_temperatures,
    check_function=check_redfish_temperatures,
    check_default_parameters={},
    check_ruleset_name="temperature",
)

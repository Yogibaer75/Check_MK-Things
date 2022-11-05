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
from .utils.dell_idrac import process_redfish_perfdata, idrac_health_state


def discovery_dell_idrac_rf_temperatures(section) -> DiscoveryResult:
    if isinstance(section, list):
        for element in section:
            data = element.get("Temperatures", {})
            for entry in data:
                if entry.get("Name"):
                    yield Service(item=entry["Name"])
    else:
        temps = section.get("Temperatures", {})
        for temp in temps:
            if temp.get("Name"):
                yield Service(item=temp.get("Name"))


def check_dell_idrac_rf_temperatures(
    item: str, params: TempParamDict, section
) -> CheckResult:
    temps = []
    if isinstance(section, list):
        for element in section:
            [temps.append(a) for a in element.get("Temperatures", [])]
    else:
        [temps.append(a) for a in section.get("Temperatures", [])]

    for temp in temps:
        if temp.get("Name") == item:
            perfdata = process_redfish_perfdata(temp)

            yield from check_temperature(
                perfdata.value,
                params,
                unique_name="idrac.temp.%s" % item,
                value_store=get_value_store(),
                dev_levels=perfdata.levels_upper,
                dev_levels_lower=perfdata.levels_lower,
            )

            dev_state, dev_msg = idrac_health_state(temp["Status"])

            yield Result(state=State(dev_state), notice=dev_msg)


register.check_plugin(
    name="dell_idrac_rf_temperatures",
    service_name="Temp %s",
    sections=["dell_idrac_rf_thermal"],
    discovery_function=discovery_dell_idrac_rf_temperatures,
    check_function=check_dell_idrac_rf_temperatures,
    check_default_parameters={},
    check_ruleset_name="temperature",
)

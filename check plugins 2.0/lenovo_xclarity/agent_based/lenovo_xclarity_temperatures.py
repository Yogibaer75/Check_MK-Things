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
from .agent_based_api.v1.type_defs import CheckResult
from .agent_based_api.v1 import register, Result, State, get_value_store
from .utils.lenovo_xclarity import (
    parse_lenovo_xclarity,
    discovery_lenovo_xclarity_multiple,
    LENOVO_STATE,
)
from .utils.temperature import (
    check_temperature,
    TempParamDict,
    TempParamType,
)

default_chassis_temperature_parameters = TempParamDict(
    device_levels_handling="devdefault",
)

register.agent_section(
    name="lenovo_xclarity_temperatures",
    parse_function=parse_lenovo_xclarity,
)


def check_lenovo_xclarity_temperatures(
    item: str, params: TempParamType, section
) -> CheckResult:
    data = section.get(item)
    if not data:
        return

    state = data.get("Status", {"State": "Unknown"}).get("State", "Unknown")
    reading = data.get("ReadingCelsius", 0)
    dev_levels = (
        data.get("UpperThresholdNonCritical"),
        data.get("UpperThresholdCritical"),
    )
    dev_levels_lower = (
        data.get("LowerThresholdNonCritical"),
        data.get("LowerThresholdCritical"),
    )
    state_txt, dev_state = LENOVO_STATE.get(state, ("State description not found", 3))
    message = "Dev state: %s" % state_txt
    yield from check_temperature(
        reading=float(reading),
        params=params,
        dev_levels=dev_levels,
        dev_levels_lower=dev_levels_lower,
        unique_name=item,
        dev_status=dev_state,
        dev_status_name=state,
        value_store=get_value_store(),
    )
    yield Result(state=State.OK, notice=message)


register.check_plugin(
    name="lenovo_xclarity_temperatures",
    service_name="Temp %s",
    sections=["lenovo_xclarity_temperatures"],
    discovery_function=discovery_lenovo_xclarity_multiple,
    check_function=check_lenovo_xclarity_temperatures,
    check_ruleset_name="temperature",
    check_default_parameters=default_chassis_temperature_parameters,
)

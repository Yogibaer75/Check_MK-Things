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

# <<<ilo_api_temp:sep(124)>>>
# 01-Inlet Ambient|21|Celsius|42|47|Enabled|OK
# Name | Value | Unit | warn | crit | State | Health

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)

from .agent_based_api.v1 import (
    register,
    Result,
    State,
    Service,
    get_value_store,
)

from .utils.temperature import (
    check_temperature,
    TempParamDict,
    TempParamType,
    render_temp,
    temp_unitsym,
)

from .utils.hp_ilo import parse_hp_ilo

register.agent_section(
    name="ilo_api_temp",
    parse_function=parse_hp_ilo,
)

default_chassis_temperature_parameters = TempParamDict(
    levels=(50.0, 60.0),
    device_levels_handling="best",
)

hp_proliant_status2cmk_map = {
    "unknown": 3,
    "other": 3,
    "none": 3,
    "ok": 0,
    "degraded": 2,
    "failed": 2,
    "disabled": 1,
}

hp_proliant_temp2symbol = {
    "Celsius": "c",
    "Fahrenheit": "f",
    "Kelvin": "k",
}


def discovery_ilo_api_temp(section) -> DiscoveryResult:
    for element in section:
        if section[element][5] != u"Absent":
            yield Service(item=element)


def check_ilo_api_temp(item: str, params: TempParamType,
                       section) -> CheckResult:
    data = section.get(item)
    if data:
        if data[6] != "NP":
            name, value, unit, warn, crit, status_name, status = data
            devlevels = (float(warn), float(crit))
            devunit = hp_proliant_temp2symbol.get(unit)
            yield from check_temperature(
                reading=float(value),
                params=params,
                dev_levels=devlevels,
                dev_unit=devunit,
                unique_name=name,
                dev_status=hp_proliant_status2cmk_map[status.lower()],
                dev_status_name=status_name,
                value_store=get_value_store(),
            )

            yield Result(
                state=State.OK,
                summary=
                f"Device levels: {render_temp(float(warn), devunit) + temp_unitsym[devunit]} - {render_temp(float(crit), devunit) + temp_unitsym[devunit]}",
            )


register.check_plugin(
    name="ilo_api_temp",
    service_name="Temperature %s",
    sections=["ilo_api_temp"],
    discovery_function=discovery_ilo_api_temp,
    check_function=check_ilo_api_temp,
    check_ruleset_name="temperature",
    check_default_parameters=default_chassis_temperature_parameters,
)

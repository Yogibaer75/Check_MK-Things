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

from .agent_based_api.v1.type_defs import (
    CheckResult, )

from .agent_based_api.v1 import (register)

from .utils.lenovo_xclarity import (parse_lenovo_xclarity,
                                    discovery_lenovo_xclarity_multiple)
from .utils.fan import (check_fan, FanParamType)

xclarity_fan_default_levels = {
    'levels_lower': (500, 300),
}

register.agent_section(
    name="lenovo_xclarity_fans",
    parse_function=parse_lenovo_xclarity,
)


def check_lenovo_xclarity_fans(item: str, params: FanParamType,
                               section) -> CheckResult:
    if not (data := section.get(item)):
        return

    state = data.get("Status", {"State": "Unknown"}).get("State", "Unknown")
    reading = float(data.get("Reading", 0))

    dev_levels = (data.get("UpperThresholdNonCritical"),
                  data.get("UpperThresholdCritical"))
    dev_levels_lower = (data.get("LowerThresholdNonCritical"),
                        data.get("LowerThresholdCritical"))

    yield from check_fan(
        reading,
        params,
        dev_levels=dev_levels,
        dev_levels_lower=dev_levels_lower,
        dev_status=0 if state == "Enabled" else 1,
        dev_status_name=state,
    )


register.check_plugin(
    name="lenovo_xclarity_fans",
    service_name="%s",
    sections=["lenovo_xclarity_fans"],
    discovery_function=discovery_lenovo_xclarity_multiple,
    check_function=check_lenovo_xclarity_fans,
    check_ruleset_name="fans",
    check_default_parameters=xclarity_fan_default_levels,
)

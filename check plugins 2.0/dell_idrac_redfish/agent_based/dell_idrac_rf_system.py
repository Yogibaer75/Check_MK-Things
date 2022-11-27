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

from .agent_based_api.v1 import register, Result, State, Service

from .utils.dell_idrac import parse_dell_idrac_rf, idrac_health_state

register.agent_section(
    name="dell_idrac_rf_system",
    parse_function=parse_dell_idrac_rf,
)


def discovery_dell_idrac_rf_system(section) -> DiscoveryResult:
    if isinstance(section, list):
        for element in section:
            yield Service(item=element["Id"])
    else:
        yield Service(item=section["Id"])


def check_dell_idrac_rf_system(item: str, section) -> CheckResult:
    power_state_map = {
        "Off": (
            1,
            "The components within the chassis has no power, except some components may continue to have AUX power such as management controller.",
        ),
        "On": (0, "The components within the chassis has power on."),
        "PoweringOff": (
            1,
            "A temporary state between On and Off. The components within the chassis can take time to process the power off action.",
        ),
        "PoweringOn": (
            0,
            "A temporary state between Off and On. The components within the chassis can take time to process the power on action.",
        ),
    }

    systems = {}
    if isinstance(section, list):
        for element in section:
            systems.setdefault(element["Id"], element)
    else:
        systems.setdefault(section["Id"], section)

    data = systems.get(item, None)
    if data is None:
        return

    sys_msg = "Model: %s, Serial: %s" % (data.get("Model"), data.get("SerialNumber"))
    yield Result(state=State(0), summary=sys_msg)

    pow_state, pow_msg = power_state_map.get(
        data["PowerState"], (3, "No power state found")
    )
    yield Result(
        state=State(pow_state),
        summary="PowerState: %s" % data["PowerState"],
    )
    yield Result(state=State(0), notice=pow_msg)

    if data.get("Status"):
        dev_state, dev_msg = idrac_health_state(data["Status"])
        yield Result(state=State(dev_state), notice=dev_msg)


register.check_plugin(
    name="dell_idrac_rf_system",
    service_name="System %s",
    sections=["dell_idrac_rf_system"],
    discovery_function=discovery_dell_idrac_rf_system,
    check_function=check_dell_idrac_rf_system,
)

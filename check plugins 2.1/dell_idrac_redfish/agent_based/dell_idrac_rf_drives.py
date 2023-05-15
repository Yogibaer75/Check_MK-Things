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

from .utils.dell_idrac import parse_dell_idrac_rf_multiple, idrac_health_state

register.agent_section(
    name="dell_idrac_rf_drives",
    parse_function=parse_dell_idrac_rf_multiple,
)


def discovery_dell_idrac_rf_drives(section) -> DiscoveryResult:
    for key in section.keys():
        yield Service(item=section[key]["Name"])


def check_dell_idrac_rf_drives(item: str, section) -> CheckResult:
    data = None
    for key in section.keys():
        if item == section[key]["Name"]:
            data = section.get(key, None)
    if data is None:
        return

    disc_msg = "Size: %0.0fGB, Speed %s Gbs" % (
        data.get("CapacityBytes", 0) / 1024 / 1024 / 1024,
        data.get("CapableSpeedGbs", 0),
    )

    if data.get("MediaType") == "SSD":
        if data.get("PredictedMediaLifeLeftPercent"):
            disc_msg = disc_msg + ", Media Life Left: %d%%" % (
                int(data.get("PredictedMediaLifeLeftPercent", 0))
            )

    yield Result(state=State(0), summary=disc_msg)

    dev_state, dev_msg = idrac_health_state(data["Status"])
    status = dev_state
    message = dev_msg

    yield Result(state=State(status), notice=message)


register.check_plugin(
    name="dell_idrac_rf_drives",
    service_name="Drive %s",
    sections=["dell_idrac_rf_drives"],
    discovery_function=discovery_dell_idrac_rf_drives,
    check_function=check_dell_idrac_rf_drives,
)

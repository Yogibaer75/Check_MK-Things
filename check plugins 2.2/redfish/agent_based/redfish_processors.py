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
)

from .utils.redfish import parse_redfish_multiple, redfish_health_state

register.agent_section(
    name="redfish_processors",
    parse_function=parse_redfish_multiple,
)


def discovery_redfish_processors(section) -> DiscoveryResult:
    """Discover single present CPUs"""
    for key in section.keys():
        if section[key].get("Status", {}).get("State") == "Absent":
            continue
        yield Service(item=section[key]["Id"])


def check_redfish_processors(item: str, section) -> CheckResult:
    """Check state of CPU"""
    data = section.get(item, None)
    if data is None:
        return

    cpu_msg = f"Type: {data.get('ProcessorType')}, Model: {data.get('Model')}"

    if "TotalCores" in data.keys():
        cpu_msg = cpu_msg + f", Cores: {data.get('TotalCores')}, \
            Threads: {data.get('TotalThreads')}, \
            Speed {data.get('OperatingSpeedMHz')} MHz"
    yield Result(state=State(0), summary=cpu_msg)

    dev_state, dev_msg = redfish_health_state(data["Status"])

    yield Result(state=State(dev_state), notice=dev_msg)


register.check_plugin(
    name="redfish_processors",
    service_name="CPU %s",
    sections=["redfish_processors"],
    discovery_function=discovery_redfish_processors,
    check_function=check_redfish_processors,
)

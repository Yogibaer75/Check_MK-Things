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
import ast
from typing import Any, Dict, Mapping
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult
from .agent_based_api.v1 import register, Result, State, Service

from .utils.redfish import redfish_health_state
Section = Dict[str, Mapping[str, Any]]


def parse_redfish_system(string_table) -> Section:
    parsed = {}
    parsed = ast.literal_eval(string_table[0][0])
    return parsed


register.agent_section(
    name="redfish_system",
    parse_function=parse_redfish_system,
)


def discover_redfish_system(section) -> DiscoveryResult:
    if section:
        yield Service()


def check_redfish_system(section) -> CheckResult:
    if not section:
        return

    state = section.get("Status", {"Health": "Unknown"})
    result_state, state_text = redfish_health_state(state)
    message = "System with SerialNr: %s, has State: %s" % (section.get("SerialNumber"), state_text)

    yield Result(state=State(result_state), summary=message)


register.check_plugin(
    name="redfish_system",
    service_name="System State",
    sections=["redfish_system"],
    discovery_function=discover_redfish_system,
    check_function=check_redfish_system,
)


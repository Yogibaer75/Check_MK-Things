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

from .agent_based_api.v1 import (
    register,
    Result,
    State,
    Service,
)


def parse_prism_hw_disks(string_table):
    import ast
    parsed = {}
    parsed = ast.literal_eval(string_table[0][0])
    return parsed


register.agent_section(
    name="prism_hw_disks",
    parse_function=parse_prism_hw_disks,
)


def discovery_prism_hw_disks(section) -> DiscoveryResult:
    for item in section:
        if section.get(item) is None:
            continue
        yield Service(item=item)


def check_prism_hw_disks(item: str, params, section) -> CheckResult:
    data = section.get(item)
    state = 0

    faulty = data["bad"]
    model = data["model"]
    serial = data["serialNumber"]
    mounted = data["mounted"]
    message = "Model: %s - Serial: %s - State: " % (model, serial)

    if faulty:
        state = 1
        message += "unhealthy"
    else:
        message += "healthy"

    if mounted:
        message += " - disk is mounted"
    else:
        message += " - disk is not mounted"

    yield Result(state=State(state), summary=message)


register.check_plugin(
    name="prism_hw_disks",
    service_name="NTNX HW Disk %s",
    sections=["prism_hw_disks"],
    check_default_parameters={
        'system_state': 0,
    },
    discovery_function=discovery_prism_hw_disks,
    check_function=check_prism_hw_disks,
    check_ruleset_name="prism_hw_disks",
)

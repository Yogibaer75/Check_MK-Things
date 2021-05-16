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

from .utils.temperature import (
    check_temperature, )

from .dell_powervault_me4 import (parse_dell_powervault_me4)

register.agent_section(
    name="dell_powervault_me4_disks",
    parse_function=parse_dell_powervault_me4,
)


def discovery_dell_powervault_me4_disks(section) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_dell_powervault_me4_disks(item: str, params, section) -> CheckResult:
    data = section.get(item)
    disk_states = {
        0: ("OK", 0),
        1: ("Degraded", 1),
        2: ("Fault", 2),
        3: ("Unknown", 3),
    }

    state_text, status_num = disk_states.get(data.get("health-numeric", 3),
                                             ("Unknown", 3))
    message = "%s disk with size %s is %s" % (data.get(
        "description", "Unknown"), data.get("size"), state_text)

    yield Result(state=State(status_num), summary=message)

    value = data.get("temperature")
    value_number = ''.join(c for c in value if (c.isdigit() or c == "."))

    yield from check_temperature(
        float(value_number),
        params,
    )


register.check_plugin(
    name="dell_powervault_me4_disks",
    service_name="Disk %s",
    sections=["dell_powervault_me4_disks"],
    check_default_parameters={
        'disk_state': 0,
        'levels': (40, 50),
    },
    discovery_function=discovery_dell_powervault_me4_disks,
    check_function=check_dell_powervault_me4_disks,
    check_ruleset_name="dell_powervault_me4_disks",
)

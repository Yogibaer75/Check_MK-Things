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

from .agent_based_api.v1.type_defs import (
    CheckResult, )

from .agent_based_api.v1 import (
    register,
    Result,
    State,
)

from .netapp_eseries import (parse_netapp_eseries,
                             discovery_netapp_eseries_multiple)

register.agent_section(
    name="netapp_eseries_power_supplies",
    parse_function=parse_netapp_eseries,
)


def check_netapp_eseries_power_supplies(item: str, params, section) -> CheckResult:
    data = section.get(item)
    status = data['status']
    state = 0
    fru_type = data['fruType']
    serial_number = data['serialNumber']

    message = "PSU %s with serial %s and type %s has status %s" % (
        item, serial_number, fru_type, status)
    if status != "optimal":
        message += "(!)"
        state = 1
    yield Result(state=State(state), summary=message)


register.check_plugin(
    name="netapp_eseries_power_supplies",
    service_name="PSU %s",
    sections=["netapp_eseries_power_supplies"],
    check_default_parameters={
        'psu_state': 0,
    },
    discovery_function=discovery_netapp_eseries_multiple,
    check_function=check_netapp_eseries_power_supplies,
    check_ruleset_name="netapp_eseries_power_supplies",
)

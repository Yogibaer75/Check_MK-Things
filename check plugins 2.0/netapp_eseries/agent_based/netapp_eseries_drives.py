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

from .utils.temperature import (
    check_temperature, )

from .agent_based_api.v1.type_defs import (
    CheckResult, )

from .agent_based_api.v1 import (
    register,
    Result,
    State,
    render,
    Metric,
)

from .netapp_eseries import (parse_netapp_eseries,
                             discovery_netapp_eseries_multiple)

register.agent_section(
    name="netapp_eseries_drives",
    parse_function=parse_netapp_eseries,
)


def check_netapp_eseries_drives(item: str, params, section) -> CheckResult:
    data = section.get(item)
    size_bytes = int(data['usableCapacity'])
    size = render.bytes(size_bytes)
    status = data['status']
    state = 0
    message = "Drive %s with size %s has status %s" % (item, size, status)
    if status != "optimal":
        message += "(!)"
        state = 1
    yield Result(state=State(state), summary=message)

    if data['driveMediaType'] == 'ssd':
        erase_count = int(data['ssdWearLife']['averageEraseCountPercent'])
        endurance_used = int(data['ssdWearLife']['percentEnduranceUsed'])
        spare_blocks = int(data['ssdWearLife']['spareBlocksRemainingPercent'])
        yield Metric("erase", erase_count, '', '', 0, 100)
        yield Metric("endurance", endurance_used, '', '', 0, 100)
        yield Metric("spareBlocks", spare_blocks, '', '', 0, 100)
        yield Result(state=State(0), summary="Disk type is SSD")

    yield from check_temperature(data["driveTemperature"]["currentTemp"],
                                 params, unique_name="netapp_eseries_temp_%s" % item)


register.check_plugin(
    name="netapp_eseries_drives",
    service_name="Drive %s",
    sections=["netapp_eseries_drives"],
    check_default_parameters={
        'drive_state': 0,
    },
    discovery_function=discovery_netapp_eseries_multiple,
    check_function=check_netapp_eseries_drives,
    check_ruleset_name="netapp_eseries_drives",
)

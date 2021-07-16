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
    render,
    get_value_store,
)

from .utils.df import (
    df_check_filesystem_single,
    FILESYSTEM_DEFAULT_LEVELS,
)

from .netapp_eseries import (parse_netapp_eseries,
                             discovery_netapp_eseries_multiple)

register.agent_section(
    name="netapp_eseries_pools",
    parse_function=parse_netapp_eseries,
)


def check_netapp_eseries_pools(item: str, params, section) -> CheckResult:
    value_store = get_value_store()
    data = section.get(item)
    state = 0

    size_total_bytes = int(data['totalRaidedSpace'])
    size_free_bytes = int(data['freeSpace'])
    size_used_bytes = int(data['usedSpace'])

    size = render.bytes(size_total_bytes)
    raid = data['raidLevel']
    status = data['state']

    message = "Pool %s with raid level %s has status %s" % (item, raid, status)
    if status != "complete":
        message += "(!)"
        state = 1
    yield Result(state=State(state), summary=message)

    yield from df_check_filesystem_single(
        value_store=value_store,
        mountpoint=item,
        size_mb=size_total_bytes / 1024 ** 2,
        avail_mb=size_free_bytes / 1024 ** 2,
        inodes_total=0,
        inodes_avail=0,
        reserved_mb=0,
        params=params,
    )


register.check_plugin(
    name="netapp_eseries_pools",
    service_name="Pool %s",
    sections=["netapp_eseries_pools"],
    check_default_parameters=FILESYSTEM_DEFAULT_LEVELS,
    discovery_function=discovery_netapp_eseries_multiple,
    check_function=check_netapp_eseries_pools,
    check_ruleset_name="filesystem",
)

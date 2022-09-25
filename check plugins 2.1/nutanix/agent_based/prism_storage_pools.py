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
    render,
    get_value_store,
)

from .utils.df import (
    df_check_filesystem_single,
    FILESYSTEM_DEFAULT_LEVELS,
)


def parse_prism_storage_pools(string_table):
    import ast
    parsed = {}
    data = ast.literal_eval(string_table[0][0])
    for element in data.get("entities"):
        parsed.setdefault(element.get("name", "unknown"), element)
    return parsed


register.agent_section(
    name="prism_storage_pools",
    parse_function=parse_prism_storage_pools,
)


def discovery_prism_storage_pools(section) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_prism_storage_pools(item: str, params, section) -> CheckResult:
    value_store = get_value_store()
    data = section.get(item)
    das_cap = float(data["usageStats"].get("storage_tier.das-sata.capacity_bytes", 0))
    das_free = float(data["usageStats"].get("storage_tier.das-sata.free_bytes", 0))
    ssd_cap = float(data["usageStats"].get("storage_tier.ssd.capacity_bytes", 0))
    ssd_free = float(data["usageStats"].get("storage_tier.ssd.free_bytes", 0))
    tot_cap = float(data["usageStats"].get("storage.capacity_bytes", 0))
    tot_free = float(data["usageStats"].get("storage.free_bytes", 0))

    yield from df_check_filesystem_single(
        value_store=value_store,
        mountpoint=item,
        size_mb=tot_cap / 1024 ** 2,
        avail_mb=tot_free / 1024 ** 2,
        inodes_total=0,
        inodes_avail=0,
        reserved_mb=0,
        params=params,
    )
    if das_cap > 0:
        message = f"SAS/SATA capacity: {render.bytes(das_cap)}, SAS/SATA free: {render.bytes(das_free)}"
        yield Result(state=State(0), summary=message)

    if ssd_cap > 0:
        message = f"SSD capacity: {render.bytes(ssd_cap)}, SSD free: {render.bytes(ssd_free)}"
        yield Result(state=State(0), summary=message)


register.check_plugin(
    name="prism_storage_pools",
    service_name="NTNX Storage %s",
    sections=["prism_storage_pools"],
    check_default_parameters=FILESYSTEM_DEFAULT_LEVELS,
    discovery_function=discovery_prism_storage_pools,
    check_function=check_prism_storage_pools,
    check_ruleset_name="filesystem",
)

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


def parse_prism_host_usage(string_table):
    import ast
    parsed = {}
    parsed = ast.literal_eval(string_table[0][0])

    return parsed


register.agent_section(
    name="prism_host_usage",
    parse_function=parse_prism_host_usage,
)


def discovery_prism_host_usage(section) -> DiscoveryResult:
    if "storage.capacity_bytes" in section:
        yield Service(item="Capacity")


def check_prism_host_usage(item: str, params, section) -> CheckResult:
    value_store = get_value_store()
    data = section
    total_sas = float(data.get("storage_tier.das-sata.capacity_bytes", 0))
    free_sas = float(data.get("storage_tier.das-sata.free_bytes", 0))
    total_ssd = float(data.get("storage_tier.ssd.capacity_bytes", 0))
    free_ssd = float(data.get("storage_tier.ssd.free_bytes", 0))
    total_bytes = float(data.get("storage.capacity_bytes", 0))
    free_bytes = float(data.get("storage.free_bytes", 0))

    yield from df_check_filesystem_single(
        value_store=value_store,
        mountpoint=item,
        size_mb=total_bytes / 1024 ** 2,
        avail_mb=free_bytes / 1024 ** 2,
        inodes_total=0,
        inodes_avail=0,
        reserved_mb=0,
        params=params,
    )
    message = f"Total SAS: {render.bytes(total_sas)}, Free SAS: {render.bytes(free_sas)}"
    yield Result(state=State(0), summary=message)
    message = f"Total SSD: {render.bytes(total_ssd)}, Free SSD: {render.bytes(free_ssd)}"
    yield Result(state=State(0), summary=message)


register.check_plugin(
    name="prism_host_usage",
    service_name="NTNX Storage %s",
    sections=["prism_host_usage"],
    check_default_parameters=FILESYSTEM_DEFAULT_LEVELS,
    discovery_function=discovery_prism_host_usage,
    check_function=check_prism_host_usage,
    check_ruleset_name="filesystem",
)

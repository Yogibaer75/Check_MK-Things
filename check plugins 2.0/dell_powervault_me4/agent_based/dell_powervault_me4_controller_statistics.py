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
from typing import Any, Mapping

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)

from cmk.base.check_api import get_bytes_human_readable

from .agent_based_api.v1 import (
    register,
    Result,
    State,
    Service,
    Metric,
)

from .dell_powervault_me4 import (parse_dell_powervault_me4)

register.agent_section(
    name="dell_powervault_me4_controller_statistics",
    parse_function=parse_dell_powervault_me4,
)


def discovery_dell_powervault_me4_controller_statistics(
        section) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_dell_powervault_me4_controller_statistics(item: str,
                                                    params: Mapping[str, Any],
                                                    section) -> CheckResult:

    data = section.get(item)
    iops = data.get("iops")
    bytespersecond = data.get("bytes-per-second-numeric")
    data_read = data.get("data-read")
    data_write = data.get("data-written")
    message = "Written data %s and read data %s, IOPS %s/s, Bytes %s/s" % (
        data_write, data_read, iops, get_bytes_human_readable(bytespersecond))
    yield Metric("iops", iops)
    yield Metric("bytes", bytespersecond)
    yield Result(state=State(0), summary=message)


register.check_plugin(
    name="dell_powervault_me4_controller_statistics",
    service_name="Controller Stats %s",
    sections=["dell_powervault_me4_controller_statistics"],
    check_default_parameters={},
    discovery_function=discovery_dell_powervault_me4_controller_statistics,
    check_function=check_dell_powervault_me4_controller_statistics,
    check_ruleset_name="dell_powervault_me4_controller_statistics",
)

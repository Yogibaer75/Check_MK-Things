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
    render,
    register,
    Result,
    State,
    Service,
    Metric,
)

from .dell_powervault_me4 import (parse_dell_powervault_me4)

register.agent_section(
    name="dell_powervault_me4_volume_statistics",
    parse_function=parse_dell_powervault_me4,
)


def discovery_dell_powervault_me4_volume_statistics(
        section) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_dell_powervault_me4_volume_statistics(item: str, params,
                                                section) -> CheckResult:
    data = section.get(item)
    sas_percent = data.get("percent-tier-sas")
    sata_percent = data.get("percent-tier-sata")
    ssd_percent = data.get("percent-tier-ssd")
    iops = data.get("iops")
    bytespersecond = data.get("bytes-per-second-numeric")
    message = "Usage SSD: %s%%, SAS %s%%, SATA %s%%, IOPS %s/s, Bytes %s/s" % (
        ssd_percent, sas_percent, sata_percent, iops,
        render.bytes(bytespersecond))

    yield Metric("ssd_usage", ssd_percent)
    yield Metric("sas_usage", sas_percent)
    yield Metric("sata_usage", sata_percent)
    yield Metric("iops", iops)
    yield Metric("bytes", bytespersecond)
    yield Result(state=State(0), summary=message)


register.check_plugin(
    name="dell_powervault_me4_volume_statistics",
    service_name="Volume Stats %s",
    sections=["dell_powervault_me4_volume_statistics"],
    check_default_parameters={
        'vol_state': 0,
    },
    discovery_function=discovery_dell_powervault_me4_volume_statistics,
    check_function=check_dell_powervault_me4_volume_statistics,
    check_ruleset_name="dell_powervault_me4_volume_statistics",
)

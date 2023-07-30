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
    register,
    Result,
    State,
    Service,
)

from .utils.redfish import parse_redfish_multiple, redfish_health_state

register.agent_section(
    name="redfish_networkports",
    parse_function=parse_redfish_multiple,
)


def discovery_redfish_networkports(section) -> DiscoveryResult:
    for key in section.keys():
        yield Service(item=section[key]["Id"])


def check_redfish_networkports(item: str, section) -> CheckResult:
    data = section.get(item, None)
    if data is None:
        return

    linkspeed = data.get("CurrentLinkSpeedMbps", 0)
    if linkspeed is None:
        linkspeed = 0

    int_msg = "Link: %s, Speed: %0.0fMbps, MAC: %s" % (
        data.get("LinkStatus"),
        linkspeed,
        ", ".join(data.get("AssociatedNetworkAddresses")),
    )
    yield Result(state=State(0), summary=int_msg)

    dev_state, dev_msg = redfish_health_state(data["Status"])
    status = dev_state
    message = dev_msg

    yield Result(state=State(status), notice=message)


register.check_plugin(
    name="redfish_networkports",
    service_name="Network Interface %s",
    sections=["redfish_networkports"],
    discovery_function=discovery_redfish_networkports,
    check_function=check_redfish_networkports,
)

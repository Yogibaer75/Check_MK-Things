#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

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
from .utils.redfish import (
    RedfishAPIData,
    parse_redfish_multiple,
    redfish_health_state,
)

register.agent_section(
    name="redfish_networkadapters",
    parse_function=parse_redfish_multiple,
)


def discovery_redfish_networkadapters(section: RedfishAPIData) -> DiscoveryResult:
    for key in section.keys():
        if section[key].get("Status", {}).get("State") in ["Absent", "Disabled"]:
            continue
        yield Service(item=section[key]["Id"])


def check_redfish_networkadapters(item: str, section: RedfishAPIData) -> CheckResult:
    data = section.get(item, None)
    if data is None:
        return

    dev_state, dev_msg = redfish_health_state(data.get("Status", {}))
    status = dev_state
    message = dev_msg

    if data.get("Model", data.get("Name")):
        net_msg = (
            f"Model: {data.get('Model', data.get('Name'))}, "
            f"SeNr: {data.get('SerialNumber')}, PartNr: {data.get('PartNumber')}"
        )
        yield Result(state=State(status), summary=net_msg)

        yield Result(state=State(status), notice=message)
    else:
        yield Result(state=State(status), summary=message)


register.check_plugin(
    name="redfish_networkadapters",
    service_name="Network Adapter %s",
    sections=["redfish_networkadapters"],
    discovery_function=discovery_redfish_networkadapters,
    check_function=check_redfish_networkadapters,
)

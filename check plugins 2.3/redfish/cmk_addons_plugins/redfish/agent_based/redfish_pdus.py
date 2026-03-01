#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""check single redfish pdu state"""

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)
from cmk_addons.plugins.redfish.lib import (
    parse_redfish_multiple,
    redfish_health_state,
    RedfishAPIData,
)

agent_section_redfish_pdus = AgentSection(
    name="redfish_rackpdus",
    parse_function=parse_redfish_multiple,
    parsed_section_name="redfish_pdus",
)


def discovery_redfish_pdus(section: RedfishAPIData) -> DiscoveryResult:
    """Discover single pdus"""
    for key in section.keys():
        if section[key].get("Status", {}).get("State") == "Absent":
            continue
        item = key.split("/")[-1]
        yield Service(item=item)


def check_redfish_pdus(item: str, section: RedfishAPIData) -> CheckResult:
    """Check single pdu state"""

    for key in section.keys():
        if key.endswith(f"/{item}"):
            item = key
            break
    data = section.get(item, None)
    if data is None:
        return
    print(data)
    firmware = data.get("FirmwareVersion")
    serial = data.get("SerialNumber")
    model = data.get("Model")
    manufacturer = data.get("Manufacturer")

    yield Result(
        state=State.OK, summary=f"PDU {manufacturer} {model} S/N {serial} FW {firmware}"
    )

    dev_state, dev_msg = redfish_health_state(data.get("Status", {}))
    yield Result(state=State(dev_state), summary=dev_msg)


check_plugin_redfish_pdus = CheckPlugin(
    name="redfish_pdus",
    service_name="PDU %s",
    sections=["redfish_pdus"],
    discovery_function=discovery_redfish_pdus,
    check_function=check_redfish_pdus,
)

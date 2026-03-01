#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)
from cmk_addons.plugins.redfish.lib import RedfishAPIData, redfish_health_state


def discovery_redfish_power_redundancy(section: RedfishAPIData) -> DiscoveryResult:
    for key in section.keys():
        if section[key].get("Redundancy", None):
            yield Service()


def check_redfish_power_redundancy(section: RedfishAPIData) -> CheckResult:
    redundancy: list[Mapping[str, Any]] = []
    for key in section.keys():
        if redundancy_element := section[key].get("Redundancy", None):
            redundancy.extend(redundancy_element)

    if not redundancy:
        return

    for element in redundancy:
        dev_state, dev_msg = redfish_health_state(element.get("Status", {}))
        yield Result(state=State(dev_state), summary=dev_msg)
        details_msg: list[str] = []
        for i in ["Name", "Mode", "MinNumNeeded", "MaxNumSupported"]:
            if value := element.get(i, None):
                details_msg.append(f"{i}: {value}")
        if (num_ps := len(element.get("RedundancySet") or [])) > 0:
            details_msg.append(f"Number of Power Supplies in Redundancy Set: {num_ps}")

        if details_msg:
            yield Result(state=State(0), notice="\n".join(details_msg))


check_plugin_redfish_power_redundancy = CheckPlugin(
    name="redfish_power_redundancy",
    service_name="Power redundancy",
    sections=["redfish_power"],
    discovery_function=discovery_redfish_power_redundancy,
    check_function=check_redfish_power_redundancy,
)

#!/usr/bin/env python3
'''check single redfish outlet state'''
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from collections.abc import Mapping
from typing import Any
from cmk.agent_based.v2 import AgentSection
from cmk_addons.plugins.redfish.lib import (
    parse_redfish_multiple,
)
from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)
from cmk_addons.plugins.redfish.lib import (
    RedfishAPIData,
    redfish_health_state,
)
from cmk.plugins.lib.elphase import (
    check_elphase,
)


agent_section_redfish_mains = AgentSection(
    name="redfish_mains",
    parse_function=parse_redfish_multiple,
    parsed_section_name="redfish_mains",
)


def discovery_redfish_mains(section: RedfishAPIData) -> DiscoveryResult:
    """Discover single sensors"""
    for key in section.keys():
        if section[key].get("Status", {}).get("State") == "Absent":
            continue
        yield Service(item=section[key]["Id"])


def check_redfish_mains(
    item: str, params: Mapping[str, Any], section: RedfishAPIData
) -> CheckResult:
    """Check single outlet state"""
    data = section.get(item, None)
    if data is None:
        return

    socket_data = {item: {
        "voltage": data.get('Voltage', {}).get('Reading', 0),
        "current": data.get('CurrentAmps', {}).get('Reading', 0),
        "power": data.get('PowerWatts', {}).get('Reading', 0),
        "frequency": data.get('FrequencyHz', {}).get('Reading', 0),
        "appower": data.get('PowerWatts', {}).get('ApparentVA', 0),
        "energy": data.get('EnergykWh', {}).get('Reading', 0) * 1000
    }}

    yield from check_elphase(
        item,
        params,
        socket_data
    )

    dev_state, dev_msg = redfish_health_state(data.get("Status", {}))
    yield Result(state=State(dev_state), notice=dev_msg)


check_plugin_redfish_mains = CheckPlugin(
    name="redfish_mains",
    service_name="Mains %s",
    sections=["redfish_mains"],
    discovery_function=discovery_redfish_mains,
    check_function=check_redfish_mains,
    check_default_parameters={},
    check_ruleset_name="ups_outphase",
)

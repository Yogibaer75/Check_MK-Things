#!/usr/bin/env python3
'''Redfish firmware inventory for HPE devices'''
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    InventoryPlugin,
    InventoryResult,
    Result,
    Service,
    State,
    TableRow,
)
from cmk_addons.plugins.redfish.lib import (
    RedfishAPIData,
    parse_redfish,
    redfish_health_state,
)

agent_section_redfish_firmware_hpe = AgentSection(
    name="redfish_firmware_hpe",
    parse_function=parse_redfish,
    parsed_section_name="redfish_firmware_hpe",
)


def inventory_redfish_firmware_hpe(section: RedfishAPIData) -> InventoryResult:
    """create inventory table for firmware"""
    path = ["hardware", "firmware", "hpe"]
    padding = len(str(len(section)))
    for entry in section:
        component_name = f"{entry.get('Id').zfill(padding)}-{entry.get('Name')}"
        yield TableRow(
            path=path,
            key_columns={
                "component": component_name,
            },
            inventory_columns={
                "version": entry.get("Version"),
                "description": entry.get("Description"),
                "updateable": entry.get("Updateable"),
            },
        )


inventory_plugin_redfish_firmware_hpe = InventoryPlugin(
    name="redfish_firmware_hpe",
    inventory_function=inventory_redfish_firmware_hpe,
)


def discovery_redfish_firmware_hpe(section: RedfishAPIData) -> DiscoveryResult:
    """discover service if data exists"""
    if section:
        yield Service()


def check_redfish_firmware_hpe(section: RedfishAPIData) -> CheckResult:
    """check the health state of the firmware"""

    padding = len(str(len(section)))
    overall_state = 0
    msg_text = ""
    info_text = ""
    info_list = []
    for entry in section:
        if not entry.get("Status"):
            continue
        component_name = f"{entry.get('Id').zfill(padding)}-{entry.get('Name')}"
        comp_state, comp_msg = redfish_health_state(entry.get("Status", {}))
        overall_state = max(overall_state, comp_state)
        if comp_state != 0:
            msg_text += f"{component_name} - {comp_msg} - "
        info_list.append(
            [component_name, comp_msg, entry.get("Version"), entry.get("Updateable")]
        )

    if not msg_text:
        msg_text = "All firmware in optimal state"

    line_bracket = "<tr>%s</tr>"
    cell_bracket = "<td>%s</td>"
    cell_seperator = ""
    headers = ("Component", "Status", "Version", "Updateable")
    info_text = f'<table>{(
        "<tr><th>"
        + "</th><th>".join(headers)
        + "</th></tr>"
        + "".join(
            [
                line_bracket
                % cell_seperator.join([cell_bracket % value for value in info_entry])
                for info_entry in info_list
            ]
        )
    )}</table>'

    yield Result(state=State(overall_state), summary=msg_text, details=info_text)


check_plugin_redfish_firmware_hpe = CheckPlugin(
    name="redfish_firmware_hpe",
    service_name="Firmware health",
    sections=["redfish_firmware_hpe"],
    discovery_function=discovery_redfish_firmware_hpe,
    check_function=check_redfish_firmware_hpe,
)

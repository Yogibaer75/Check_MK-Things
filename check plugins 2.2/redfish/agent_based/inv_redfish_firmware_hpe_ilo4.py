#!/usr/bin/env python3
'''Redfish firmware inventory for HPE devices'''
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    TableRow,
    register,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    InventoryResult,
)
from .utils.redfish import (
    RedfishAPIData,
    parse_redfish,
)


register.agent_section(
    name="redfish_firmware_hpe_ilo4",
    parse_function=parse_redfish,
    parsed_section_name="redfish_firmware_hpe_ilo4",
)


def inventory_redfish_firmware_hpe_ilo4(section: RedfishAPIData) -> InventoryResult:
    """create inventory table for firmware"""
    path = ["hardware", "firmware", "hpe"]
    padding = len(str(len(section)))
    for index, entry_id in enumerate(section):
        entry = section.get(entry_id)
        component_name = f"{str(index).zfill(padding)}-{entry[0].get('Name')}"
        yield TableRow(
            path=path,
            key_columns={
                "component": component_name,
            },
            inventory_columns={
                "version": entry[0].get("VersionString"),
                "location": entry[0].get("Location"),
            },
        )


register.inventory_plugin(
    name="redfish_firmware_hpe_ilo4",
    inventory_function=inventory_redfish_firmware_hpe_ilo4,
)

#!/usr/bin/env python3
"""HW/SW Inventory plugin for SophosXG version"""

# (c) Fabian Binder 'opensource@comnet-solutions.de' - comNET GmbH
# License: GNU General Public License v2

from typing import Dict

from cmk.agent_based.v2 import (
    InventoryPlugin,
    InventoryResult,
    Attributes,
)

Section = Dict[str, str]


def inventory_sophosxg_version(section: Section) -> InventoryResult:
    fw_version = section.get("fwversion", "Unknown")

    yield Attributes(
        path=["software", "firmware"],
        inventory_attributes={"version": fw_version},
        )


inventory_plugin_sophosxg_version = InventoryPlugin(
    name="inventory_sophosxg_version",
    inventory_function=inventory_sophosxg_version,
    sections=["sophosxg_version"],
)

#!/usr/bin/env python3

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2
from collections.abc import Mapping
from typing import Any

from cmk_addons.plugins.redfish.lib import (
    parse_redfish_multiple,
    redfish_health_state,
    RedfishAPIData,
)

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    State,
)

agent_section_redfish_drives = AgentSection(
    name="redfish_drives",
    parse_function=parse_redfish_multiple,
    parsed_section_name="redfish_drives",
)

# '@odata.id': '/redfish/v1/Systems/0/Storage/1/Drives/4' -> item: "0:1:4"
# or
# '@odata.id': '/redfish/v1/Chassis/DE00B000/Drives/0' -> item: "DE00B000:0"
# or
# 'Id' + '-' + 'Name'


def _build_drive_item(data: Mapping[str, Any]) -> tuple[str, str]:
    item1 = data["Id"] + "-" + data["Name"]
    item2 = item1
    if isinstance(data.get("@odata.id"), str):
        odataid = str(data.get("@odata.id"))
        parts = odataid.split("/")
        try:
            system_id = parts[parts.index("Systems") + 1]
            storage_id = parts[parts.index("Storage") + 1]
            drive_id = parts[parts.index("Drives") + 1]
            item2 = ":".join([system_id, storage_id, drive_id])
        except ValueError:
            # Handle case like '/redfish/v1/Chassis/DE00B000/Drives/0'
            try:
                chassis_id = parts[parts.index("Chassis") + 1]
                drive_id = parts[parts.index("Drives") + 1]
                item2 = ":".join([chassis_id, drive_id])
            except ValueError:
                # Fallback to default if neither pattern matches
                item2 = item1
    return item1, item2


def discovery_redfish_drives(params: Mapping[str, Any], section: RedfishAPIData) -> DiscoveryResult:
    for _key, data in section.items():
        if data.get("Status", {}).get("State") == "Absent":
            continue
        if not data["Name"]:
            continue
        item1, item2 = _build_drive_item(data)
        if params.get("item") == "classic":
            yield Service(item=item1)
        else:
            yield Service(item=item2)


def check_redfish_drives(item: str, section: RedfishAPIData) -> CheckResult:
    data = None
    for data_value in section.values():
        item1, item2 = _build_drive_item(data_value)
        if item in (item1, item2):
            data = data_value
            break
    if data is None:
        return

    disc_msg = (
        f"Size: {data.get('CapacityBytes', 0) / 1024 / 1024 / 1024:0.0f}GB, "
        f"Speed {data.get('CapableSpeedGbs', 0)} Gbs"
    )

    if data.get("MediaType") == "SSD":
        if data.get("PredictedMediaLifeLeftPercent"):
            disc_msg = (
                f"{disc_msg}, Media Life Left: {int(data.get('PredictedMediaLifeLeftPercent', 0))}%"
            )
            yield Metric("media_life_left", int(data.get("PredictedMediaLifeLeftPercent")))
        else:
            disc_msg = f"{disc_msg}, no SSD Media information available"

    yield Result(state=State(0), summary=disc_msg)

    dev_state, dev_msg = redfish_health_state(data.get("Status", {}))
    yield Result(state=State(dev_state), notice=dev_msg)


check_plugin_redfish_drives = CheckPlugin(
    name="redfish_drives",
    service_name="Drive %s",
    sections=["redfish_drives"],
    discovery_function=discovery_redfish_drives,
    discovery_ruleset_name="discovery_redfish_drives",
    discovery_default_parameters={"item": "classic"},
    check_function=check_redfish_drives,
)

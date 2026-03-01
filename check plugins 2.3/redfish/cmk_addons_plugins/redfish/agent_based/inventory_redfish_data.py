#!/usr/bin/env python3
# Copyright (C) 2023 Checkmk GmbH - License: Checkmk Enterprise License
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping, Sequence
from typing import Any

from cmk.agent_based.v2 import InventoryPlugin, InventoryResult, TableRow
from cmk_addons.plugins.redfish.lib import RedfishAPIData

IDSET = set[tuple[str, str, str, str, str, str]]


def _extract_odata_ids(
    data: None | RedfishAPIData | Sequence[Mapping[str, Any]], ids_set: IDSET
) -> IDSET:
    if data is None or isinstance(data, (str, int, float, bool)):
        return ids_set

    if isinstance(data, Mapping):
        for key, value in data.items():
            if key == "@odata.id" and isinstance(value, str):
                if "Oem" not in value:
                    key_name = data.get("Name")
                    if key_name:
                        ids_set.add(
                            (
                                value,
                                key_name,
                                (data.get("SerialNumber") or "nothing set").strip(),
                                (data.get("PartNumber") or "nothing set").strip(),
                                (data.get("Manufacturer") or "nothing set").strip(),
                                (data.get("Model") or "nothing set").strip(),
                            )
                        )
            else:
                ids_set = _extract_odata_ids(value, ids_set)
    else:
        for item in data:
            ids_set = _extract_odata_ids(item, ids_set)

    return ids_set


def inventory_redfish_data(
    section_redfish_storage: None | RedfishAPIData,
    section_redfish_processors: None | RedfishAPIData,
    section_redfish_drives: None | RedfishAPIData,
    section_redfish_psu: None | RedfishAPIData,
    section_redfish_memory: None | RedfishAPIData,
    section_redfish_power: None | RedfishAPIData,
    section_redfish_thermal: None | RedfishAPIData,
    section_redfish_networkadapters: None | RedfishAPIData,
) -> InventoryResult:
    result_path = ["redfish"]

    odata_ids_set = set()  # Ein Set verwenden, um Duplikate automatisch zu vermeiden
    odata_ids_set = _extract_odata_ids(section_redfish_processors, odata_ids_set)
    odata_ids_set = _extract_odata_ids(section_redfish_storage, odata_ids_set)
    odata_ids_set = _extract_odata_ids(section_redfish_drives, odata_ids_set)
    odata_ids_set = _extract_odata_ids(section_redfish_psu, odata_ids_set)
    odata_ids_set = _extract_odata_ids(section_redfish_memory, odata_ids_set)
    odata_ids_set = _extract_odata_ids(section_redfish_power, odata_ids_set)
    odata_ids_set = _extract_odata_ids(section_redfish_thermal, odata_ids_set)
    odata_ids_set = _extract_odata_ids(section_redfish_networkadapters, odata_ids_set)

    for path, name, serial, part_number, manufacturer, model in odata_ids_set:
        if (
            serial in ("nothing set", "NOT AVAILABLE")
            and part_number in ("nothing set", "NOT AVAILABLE")
            and manufacturer == "nothing set"
            and model == "nothing set"
        ):
            continue
        if path.startswith("/redfish/"):
            segments = (
                path.replace("#", "")
                .replace(":", "-")
                .replace(".", "_")
                .replace("'", "")
                .replace("(", "_")
                .replace(")", "_")
                .replace("%", "_")
                .strip("/")
                .split("/")
            )
            result_path = [element for element in segments if element != ""]
        item_id = result_path.pop()
        if result_path[0] == "redfish":
            result_path = result_path[1:]
        if result_path[0] == "v1":
            result_path = result_path[1:]
        final_path = ["hardware"] + result_path
        yield TableRow(
            path=final_path,
            key_columns={"id": item_id},
            inventory_columns={
                "name": name,
                "serial": serial,
                "part_number": part_number,
                "manufacturer": manufacturer,
                "model": model,
            },
        )


inventory_plugin_redfish_data = InventoryPlugin(
    name="redfish_data",
    sections=[
        "redfish_storage",
        "redfish_processors",
        "redfish_drives",
        "redfish_psu",
        "redfish_memory",
        "redfish_power",
        "redfish_thermal",
        "redfish_networkadapters",
    ],
    inventory_function=inventory_redfish_data,
)

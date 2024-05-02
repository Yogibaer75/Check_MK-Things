#!/usr/bin/env python3
"""helper functions for all Dell Powervault checks"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from collections.abc import Mapping
import json
from typing import Any
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import StringTable

Section = Mapping[str, Any]


def load_json(string_table: StringTable) -> Section:
    """load JSON into dictionary"""
    try:
        return json.loads(string_table[0][0])
    except (IndexError, json.decoder.JSONDecodeError):
        return {}


def parse_dell_powervault_me4(string_table: StringTable) -> Section:
    """parse the raw data into dictionary"""
    items = {
        "controllers": "durable-id",
        "pools": "name",
        "volumes": "durable-id",
        "fan": "durable-id",
        "enclosure-fru": "fru-location",
        "power-supplies": "durable-id",
        "sensors": "durable-id",
        "system": "system-name",
        "drives": "durable-id",
        "controller-statistics": "durable-id",
        "volume-statistics": "volume-name",
        "port": "durable-id",
    }
    parsed = {}
    data = load_json(string_table)

    for key, dev_id in items.items():
        if data.get(key, False):
            for element in data.get(key):
                item = element.get(dev_id)
                if item:
                    parsed.setdefault(item, element)

    return parsed

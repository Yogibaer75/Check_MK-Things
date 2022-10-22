#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.
import ast
from typing import Any, Dict, Mapping, Tuple
from ..agent_based_api.v1.type_defs import DiscoveryResult
from ..agent_based_api.v1 import Service

Section = Dict[str, Mapping[str, Any]]
State_dict = Dict[str, Tuple[str, int]]

LENOVO_STATE: State_dict = {
    "Enabled": ("This function or resource has been enabled.", 0),
    "Disabled": ("This function or resource has been disabled.", 1),
    "StandbyOffline": ("This function or resource is enabled, but awaiting an external action to activate it.", 0),
    "StandbySpare": ("This function or resource is part of a redundancy set and is awaiting a failover or other external action to activate it.", 0),
    "InTest": ("This function or resource is undergoing testing.", 1),
    "Starting": ("This function or resource is starting.", 1),
    "Absent": ("This function or resource is not present or not detected.", 1),
    "UnavailableOffline": ("This function or resource is present but cannot be used.", 1),
    "Deferring": ("The element will not process any commands but will queue new requests.", 1),
    "Quiesced": ("The element is enabled but only processes a restricted set of commands.", 1),
    "Updating": ("The element is updating and may be unavailable or degraded.", 1),
}


def parse_lenovo_xclarity(string_table) -> Section:
    parsed = {}
    data = ast.literal_eval(string_table[0][0])
    for element in data:
        device = element.get("Name", "Unknown")
        parsed.setdefault(device, element)
    return parsed


def discovery_lenovo_xclarity_multiple(section: Section) -> DiscoveryResult:
    for item in section.items():
        key, data = item
        if data.get("Status", {}).get("State") == "Absent":
            continue
        yield Service(item=key)

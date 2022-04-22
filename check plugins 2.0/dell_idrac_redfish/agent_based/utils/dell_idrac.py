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

from typing import Optional, NamedTuple, Tuple
from ..agent_based_api.v1.type_defs import (
    DiscoveryResult, )

from ..agent_based_api.v1 import (
    Service, )

Levels = Optional[Tuple[float, float]]


class Perfdata(NamedTuple):
    name: str
    value: float
    levels_upper: Levels
    levels_lower: Levels
    boundaries: Optional[Tuple[Optional[float], Optional[float]]]


def parse_dell_idrac_rf(string_table):
    import ast

    parsed = {}
    parsed = ast.literal_eval(string_table[0][0])

    return parsed


def parse_dell_idrac_rf_multiple(string_table):
    import ast

    parsed = {}
    for line in string_table:
        entry = ast.literal_eval(line[0])
        parsed.setdefault(entry.get("Id"), entry)

    return parsed


def discovery_dell_idrac_rf_multiple(section) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def _try_convert_to_float(value: str) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def idrac_health_state(state):
    health_map = {
        "OK": (0, "Normal"),
        "Warning": (1, "A condition requires attention."),
        "Critical": (2, "A critical condition requires immediate attention."),
    }

    state_map = {
        "Enabled": (0, "This resource is enabled."),
        "Disabled": (1, "This resource is disabled."),
        "StandbyOffline": (1, "This resource is enabled but awaits an external action to activate it."),
        "StandbySpare": (0, "This resource is part of a redundancy set and awaits a failover or other external action to activate it."),
        "InTest": (0, "This resource is undergoing testing, or is in the process of capturing information for debugging."),
        "Starting": (0, "This resource is starting."),
        "Absent": (1, "This resource is either not present or detected."),
    }

    dev_state = 0
    dev_msg = []
    for key in state.keys():
        if key in ["Health"]:
            if state[key] == None:
                continue
            temp_state, state_msg = health_map.get(state[key])
            state_msg = "Component State: %s" % state_msg
        elif key == "HealthRollup":
            if state[key] == None:
                continue
            temp_state, state_msg = health_map.get(state[key])
            state_msg = "Rollup State: %s" % state_msg
        elif key == "State":
            temp_state, state_msg = state_map.get(state[key])
        dev_state = max(dev_state, temp_state)
        dev_msg.append(state_msg)

    return dev_state, ", ".join(dev_msg)


def process_redfish_perfdata(entry):
    name = entry.get("Name")

    if "Reading" in entry.keys():
        value = entry.get("Reading", 0)
    elif "ReadingVolts" in entry.keys():
        value = entry.get("ReadingVolts", 0)
    elif "ReadingCelsius" in entry.keys():
        value = entry.get("ReadingCelsius", 0)

    value = _try_convert_to_float(value)
    min_range = _try_convert_to_float(entry.get("MinReadingRange", None))
    max_range = _try_convert_to_float(entry.get("MaxReadingRange", None))
    min_warn = _try_convert_to_float(entry.get("LowerThresholdNonCritical", None))
    min_crit = _try_convert_to_float(entry.get("LowerThresholdCritical", None))
    upper_warn = _try_convert_to_float(entry.get("UpperThresholdNonCritical", None))
    upper_crit = _try_convert_to_float(entry.get("UpperThresholdCritical", None))

    if min_warn is None and min_crit is not None:
        min_warn = min_crit

    if upper_warn is None and upper_crit is not None:
        upper_warn = upper_crit

    if min_warn is not None and min_crit is None:
        min_crit = float("-inf")

    if upper_warn is not None and upper_crit is None:
        upper_crit = float("inf")

    def optional_tuple(warn: Optional[float], crit: Optional[float]) -> Levels:
        assert (warn is None) == (crit is None)
        if warn is not None and crit is not None:
            return warn, crit
        return None

    return Perfdata(
        name,
        value,
        levels_upper=optional_tuple(upper_warn, upper_crit),
        levels_lower=optional_tuple(min_warn, min_crit),
        boundaries=(
            min_range,
            max_range,
        ),
    )

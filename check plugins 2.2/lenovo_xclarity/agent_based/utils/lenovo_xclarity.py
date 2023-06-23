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
from typing import Any, Dict, Mapping, NamedTuple, Optional, Tuple, TypedDict, Union
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    DiscoveryResult,
    CheckResult,
)
from cmk.base.plugins.agent_based.agent_based_api.v1 import Service, check_levels

Section = Dict[str, Mapping[str, Any]]
State_dict = Dict[str, Tuple[str, int]]
Levels = Optional[Tuple[float, float]]

LevelModes = str
TwoLevelsType = Tuple[Optional[float], Optional[float]]
FourLevelsType = Tuple[
    Optional[float], Optional[float], Optional[float], Optional[float]
]
LevelsType = Union[TwoLevelsType, FourLevelsType]
FanParamDict = TypedDict(
    "TempParamDict",
    {
        "levels": TwoLevelsType,
        "levels_lower": TwoLevelsType,
        "device_levels_handling": LevelModes,
    },
    total=False,
)
FanParamType = Union[None, TwoLevelsType, FourLevelsType, FanParamDict]

LENOVO_STATE: State_dict = {
    "Enabled": ("This function or resource has been enabled.", 0),
    "Disabled": ("This function or resource has been disabled.", 1),
    "StandbyOffline": (
        "This function or resource is enabled, but awaiting an external action to activate it.",
        0,
    ),
    "StandbySpare": (
        "This function or resource is part of a redundancy set and is awaiting a failover or other external action to activate it.",
        0,
    ),
    "InTest": ("This function or resource is undergoing testing.", 1),
    "Starting": ("This function or resource is starting.", 1),
    "Absent": ("This function or resource is not present or not detected.", 1),
    "UnavailableOffline": (
        "This function or resource is present but cannot be used.",
        1,
    ),
    "Deferring": (
        "The element will not process any commands but will queue new requests.",
        1,
    ),
    "Quiesced": (
        "The element is enabled but only processes a restricted set of commands.",
        1,
    ),
    "Updating": ("The element is updating and may be unavailable or degraded.", 1),
}


class Perfdata(NamedTuple):
    name: str
    value: float
    levels_upper: Levels
    levels_lower: Levels
    boundaries: Optional[Tuple[Optional[float], Optional[float]]]


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


def _try_convert_to_float(value: str) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def xclarity_health_state(state: Dict[str, Mapping[str, Any]]):
    health_map = {
        "OK": (0, "Normal"),
        "Warning": (1, "A condition requires attention."),
        "Critical": (2, "A critical condition requires immediate attention."),
    }

    state_map = {
        "Enabled": (0, "This resource is enabled."),
        "Disabled": (1, "This resource is disabled."),
        "StandbyOffline": (
            1,
            "This resource is enabled but awaits an external action to activate it.",
        ),
        "StandbySpare": (
            0,
            "This resource is part of a redundancy set and awaits a failover or other external action to activate it.",
        ),
        "InTest": (
            0,
            "This resource is undergoing testing, or is in the process of capturing information for debugging.",
        ),
        "Starting": (0, "This resource is starting."),
        "Absent": (1, "This resource is either not present or detected."),
        "Updating": (1, "The element is updating and may be unavailable or degraded"),
        "UnvailableOffline": (
            1,
            "This function or resource is present but cannot be used",
        ),
        "Deferring": (
            0,
            "The element will not process any commands but will queue new requests",
        ),
        "Quiesced": (
            0,
            "The element is enabled but only processes a restricted set of commands",
        ),
    }

    dev_state = 0
    dev_msg = []
    state_msg = ""
    temp_state = 0
    for key in state.keys():
        if key in ["Health"]:
            if state[key] is None:
                continue
            temp_state, state_msg = health_map.get(state[key])
            state_msg = "Component State: %s" % state_msg
        elif key == "HealthRollup":
            if state[key] is None:
                continue
            temp_state, state_msg = health_map.get(state[key])
            state_msg = "Rollup State: %s" % state_msg
        elif key == "State":
            if state[key] is None:
                continue
            temp_state, state_msg = state_map.get(state[key])
        dev_state = max(dev_state, temp_state)
        dev_msg.append(state_msg)

    if dev_msg == []:
        dev_msg.append("No state information found")

    return dev_state, ", ".join(dev_msg)


def process_xclarity_perfdata(entry):
    name = entry.get("Name")

    value = "0"
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


def xclarity_check_fan_percent(perfdata: Perfdata, params: FanParamType) -> CheckResult:
    return check_levels(
        perfdata.value,
        levels_upper=perfdata.levels_upper,
        levels_lower=perfdata.levels_lower,
        metric_name="perc",
        label="Speed",
        render_func=lambda v: "%.1f%%" % v,
        boundaries=(0, 100),
    )


def xclarity_check_fan_rpm(perfdata: Perfdata, params: FanParamType) -> CheckResult:
    return check_levels(
        perfdata.value,
        levels_upper=perfdata.levels_upper,
        levels_lower=perfdata.levels_lower,
        metric_name="fan",
        label="Speed",
        render_func=lambda v: "%.1f rpm" % v,
        boundaries=perfdata.boundaries,
    )

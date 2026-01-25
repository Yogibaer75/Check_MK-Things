#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
"""check for BACS battery status"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2
from typing import Any, List, Mapping

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Service,
    SNMPSection,
    SNMPTree,
    StringTable,
    check_levels,
    startswith,
)

bacs_battery_default_levels = {
    "voltage": ("fixed", (14, 15)),
    "voltage_lower": ("fixed", (10, 9)),
    "temp": ("fixed", (40, 50)),
    "temp_lower": ("fixed", (10, 5)),
    "resistance": ("fixed", (15, 18)),
}

Section = Mapping[str, Any]


def parse_bacs_battery(string_table: List[StringTable]) -> Section:
    """parse data into dict"""
    scale_temp = 10.0
    scale_volt = 100.0
    scale_res = 100.0
    data, _thresholds = string_table
    parsed = {}
    try:
        if int(data[0][0]) == 0:
            modifier = 1
        else:
            modifier = 0
    except IndexError:
        modifier = 0

    for bat_id, bat_volt, bat_temp, bat_res, bat_state in data:
        parsed[str(int(bat_id) + modifier)] = (
            int(bat_volt) / scale_volt,
            int(bat_temp) / scale_temp,
            int(bat_res) / scale_res,
            int(bat_state),
        )
    return parsed


snmp_section_bacs_battery = SNMPSection(
    name="bacs_battery",
    detect=startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.2.1.33"),
    parse_function=parse_bacs_battery,
    fetch=[
        SNMPTree(
            base=".1.3.6.1.2.1.33.5.2.5.1",
            oids=[
                "1",  # bacsModuleIndex
                "2",  # bacsModuleVoltage
                "3",  # bacsModuleTemperture
                "5",  # bacsModuleResistance
                "6",  # bacsModuleState
            ],
        ),
        SNMPTree(
            base=".1.3.6.1.2.1.33.5",
            oids=[
                "1",
            ],
        ),
    ],
)


def inventory_bacs_battery(section: Section) -> DiscoveryResult:
    """discover one service per battery"""
    for item in section:
        yield Service(item=item)


def check_bacs_battery(item: str, params, section: Section) -> CheckResult:
    """check state of a single battery"""
    data = section.get(item)
    if not data:
        return

    for key in bacs_battery_default_levels:
        if isinstance(params.get(key), tuple) and not isinstance(params.get(key)[0], str):
            params[key] = ("fixed", params[key])

    bat_volt, bat_temp, bat_res, _bat_status = data

    yield from check_levels(
        bat_temp,
        levels_lower=params.get("temp_lower", ("no_levels", None)),
        levels_upper=params.get("temp", ("no_levels", None)),
        metric_name="temp",
        label="Temperature",
        render_func=lambda v: f"{v:.1f}°C",
    )

    yield from check_levels(
        bat_res,
        levels_upper=params.get("resistance", ("no_levels", None)),
        metric_name="resistance",
        label="Resistance",
        render_func=lambda v: f"{v:.2f}mOhm",
    )

    yield from check_levels(
        bat_volt,
        levels_upper=params.get("voltage", ("no_levels", None)),
        levels_lower=params.get("voltage_lower", ("no_levels", None)),
        metric_name="voltage",
        label="Voltage",
        render_func=lambda v: f"{v:.2f}V",
    )


check_plugin_bacs_battery = CheckPlugin(
    name="bacs_battery",
    check_function=check_bacs_battery,
    discovery_function=inventory_bacs_battery,
    service_name="BACS Module %s",
    check_default_parameters=bacs_battery_default_levels,
    check_ruleset_name="bacs",
)

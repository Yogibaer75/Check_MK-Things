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
    SimpleSNMPSection,
    SNMPTree,
    StringTable,
    check_levels,
    get_value_store,
    startswith,
)
from cmk.plugins.lib.temperature import check_temperature

bacs_battery_default_levels = {
    "levels": (55, 60),
    "voltage": (14, 15),
    "voltage_lower": (10, 9),
    "temp": (40, 50),
    "temp_lower": (10, 5),
    "resistance": (15, 18),
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


snmp_section_bacs_battery = SimpleSNMPSection(
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

    if isinstance(params, tuple):
        params = {"levels": params}

    params_temp = {}
    if "temp" in params:
        params_temp["levels"] = params["temp"]
    if "levels" in params:
        params_temp["levels"] = params["levels"]
    if "temp_lower" in params:
        params_temp["levels_lower"] = params["temp_lower"]

    bat_volt, bat_temp, bat_res, _bat_status = data
    res_warn, res_crit = params["resistance"]
    volt_warn, volt_crit = params["voltage"]
    volt_warn_lower, volt_crit_lower = params["voltage_lower"]

    yield from check_temperature(
        bat_temp,
        params_temp,
        unique_name=f"bacs_temperature_{item}",
        value_store=get_value_store(),
    )

    yield from check_levels(
        bat_res,
        levels_upper=(res_warn, res_crit),
        metric_name="resistance",
        label="Resistance",
        render_func=lambda v: f"{v:.2f}mOhm",
    )

    yield from check_levels(
        bat_volt,
        levels_upper=(volt_warn, volt_crit),
        levels_lower=(volt_warn_lower, volt_crit_lower),
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

#!/usr/bin/env python3
"""Oracle ILOM sensor checks"""
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from typing import Dict, List, NamedTuple

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    OIDEnd,
    Result,
    Service,
    SNMPSection,
    SNMPTree,
    State,
    StringTable,
    check_levels,
    contains,
    get_value_store,
)
from cmk.plugins.lib.temperature import (
    TempParamDict,
    check_temperature,
)
from cmk_addons.plugins.oracle_ilom.lib import process_oracle_ilom_perfdata
from typing_extensions import TypedDict

oracle_ilom_map_unit = {
    "1": " Other",
    "2": " Unknown",
    "3": "c",
    "4": "f",
    "5": "k",
    "6": "v",
    "7": "a",
    "8": "w",
    "20": "rpm",
    "21": "frequency",
}

oracle_ilom_unit_perf = {
    "w": "power",
    "rpm": "fan",
    "v": "voltage",
}

oracle_ilom_map_type = {
    "1": "other",
    "2": "unknown",
    "3": "temperature",
    "4": "voltage",
    "5": "current",
    "6": "tachometer",
    "7": "counter",
    "8": "switch",
    "9": "lock",
    "10": "humidity",
    "11": "smoke",
    "12": "presence",
    "13": "airflow",
}

oracle_ilom_map_state = {
    "1": (2, "Critical"),
    "2": (2, "Major"),
    "3": (1, "Minor"),
    "4": (3, "indeterminate"),
    "5": (1, "Warning"),
    "6": (1, "Pending"),
    "7": (0, "Cleared"),
}

LevelModes = str
TwoLevelsType = tuple[str, tuple[float | None, float | None]]


class ILOMSens(NamedTuple):
    """ILOM sensor named tuple"""

    sensor_type: str
    sensor_state: str
    availability: str
    sensor_unit: str
    sensor_exponent: int
    sensor_value_str: str
    sensor_lower_warn_value: int
    sensor_upper_warn_value: int
    sensor_lower_crit_value: int
    sensor_upper_crit_value: int
    sensor_lower_fatal_value: int
    sensor_upper_fatal_value: int


class IlomParamDict(TypedDict, total=False):
    """Parameter from generic ILOM Rule"""

    levels: TwoLevelsType
    levels_lower: TwoLevelsType
    device_levels_handling: LevelModes


Section = Dict[str, ILOMSens]


def parse_oracle_ilom(string_table: List[StringTable]) -> Section:
    """parse data into dictionary"""
    parsed = {}
    entities = {}
    sensors, entity, types = string_table

    for entity_id, entity_state, entity_alarm, entity_name in entity:
        entities[entity_id] = {
            "name": entity_name,
            "state": entity_state,
            "alarm": entity_alarm,
        }

    for type_id, type_entry in types:
        if type_id in entities:
            entities[type_id].update(
                {"type": oracle_ilom_map_type.get(type_entry, "other")}
            )

    for (
        sensor_id,
        sensor_unit,
        sensor_exponent,
        sensor_value_str,
        sensor_lower_warn_value,
        sensor_upper_warn_value,
        sensor_lower_crit_value,
        sensor_upper_crit_value,
        sensor_lower_fatal_value,
        sensor_upper_fatal_value,
        _sensor_bit_mask,
    ) in sensors:
        sensor_name = f"Sensor {sensor_id} {entities[sensor_id]['name'].strip()}"
        parsed[sensor_name] = ILOMSens(
            sensor_type=entities[sensor_id]["type"],
            sensor_state=entities[sensor_id]["alarm"],
            availability=entities[sensor_id]["state"],
            sensor_unit=oracle_ilom_map_unit.get(sensor_unit, " Other"),
            sensor_exponent=sensor_exponent,
            sensor_value_str=sensor_value_str,
            sensor_lower_warn_value=sensor_lower_warn_value,
            sensor_upper_warn_value=sensor_upper_warn_value,
            sensor_lower_crit_value=sensor_lower_crit_value,
            sensor_upper_crit_value=sensor_upper_crit_value,
            sensor_lower_fatal_value=sensor_lower_fatal_value,
            sensor_upper_fatal_value=sensor_upper_fatal_value,
        )
    return parsed


snmp_section_oracle_ilom = SNMPSection(
    name="oracle_ilom",
    parse_function=parse_oracle_ilom,
    detect=contains(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.42.2.200"),
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.42.2.70.101.1.1.8.1",
            oids=[
                OIDEnd(),
                "1",  # sunPlatNumericSensorBaseUnits
                "2",  # sunPlatNumericSensorExponent
                "4",  # sunPlatNumericSensorCurrent
                "8",  # sunPlatNumericSensorLowerThresholdNonCritical
                "9",  # sunPlatNumericSensorUpperThresholdNonCritical
                "10",  # sunPlatNumericSensorLowerThresholdCritical
                "11",  # sunPlatNumericSensorUpperThresholdCritical
                "12",  # sunPlatNumericSensorLowerThresholdFatal
                "13",  # sunPlatNumericSensorUpperThresholdFatal
                "15",  # sunPlatNumericSensorEnabledThresholds
            ],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.42.2.70.101.1.1.2.1",
            oids=[
                OIDEnd(),
                "2",  # sunPlatEquipmentOperationalState
                "3",  # sunPlatEquipmentAlarmStatus
                "5",  # sunPlatEquipmentLocationName
            ],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.42.2.70.101.1.1.6.1",
            oids=[
                OIDEnd(),
                "2",  # sunPlatEquipmentLocationName
            ],
        ),
    ],
)


def _parse_levels(
    levels: tuple[ str, tuple[float | None, float | None] ]| tuple[ str, None ]| None = None,
) -> tuple[float, float] | None:
    if levels is None:
        return None

    if isinstance(levels[0], str):
        if levels[0] == "no_levels":
            return None
        if levels[0] == "fixed":
            warn, crit = levels[1]

    if warn is None or crit is None:
        return None

    return warn, crit


def discover_oracle_ilom(params, section: Dict[str, ILOMSens]) -> DiscoveryResult:
    """for every sensor one service is discovered"""
    for key, values in section.items():
        if values.availability == "2" and values.sensor_type == params.get("value"):
            yield Service(item=key, parameters={})


def check_oracle_ilom(
    item: str, params: IlomParamDict, section: Dict[str, ILOMSens]
) -> CheckResult:
    """check the state of a non temperature sensor"""
    data = section.get(item)
    if data:
        state, state_readable = oracle_ilom_map_state.get(
            data.sensor_state, (3, "unknown")
        )
        unit = data.sensor_unit
        perfdata = process_oracle_ilom_perfdata(data)
        usr_levels_upper = _parse_levels(params.get("levels", ('no_levels', None)))
        usr_levels_lower = _parse_levels(params.get("levels_lower", ('no_levels', None)))
        device_levels_handling = params.get("device_levels_handling", "usrdefault")
        if device_levels_handling == "usrdefault":
            levels_upper = (
                usr_levels_upper
                if usr_levels_upper and len(usr_levels_upper) > 1
                else (
                    perfdata.levels_upper[1]
                    if perfdata.levels_upper and len(perfdata.levels_upper) > 1
                    else None
                )
            )
            levels_lower = (
                usr_levels_lower
                if usr_levels_lower and len(usr_levels_lower) > 1
                else (
                    perfdata.levels_lower[1]
                    if perfdata.levels_lower and len(perfdata.levels_lower) > 1
                    else None
                )
            )
        elif device_levels_handling == "devdefault":
            levels_upper = (
                perfdata.levels_upper[1]
                if perfdata.levels_upper and len(perfdata.levels_upper) > 1
                else usr_levels_upper
            )
            levels_lower = (
                perfdata.levels_lower[1]
                if perfdata.levels_lower and len(perfdata.levels_lower) > 1
                else usr_levels_lower
            )
        elif device_levels_handling == "dev":
            levels_upper = (
                perfdata.levels_upper[1]
                if perfdata.levels_upper and len(perfdata.levels_upper) > 1
                else None
            )
            levels_lower = (
                perfdata.levels_lower[1]
                if perfdata.levels_lower and len(perfdata.levels_lower) > 1
                else None
            )
        elif device_levels_handling == "usr":
            levels_upper = usr_levels_upper
            levels_lower = usr_levels_lower
        infotext = f"status: {state_readable}"
        yield from check_levels(
            perfdata.value,
            metric_name=oracle_ilom_unit_perf.get(data.sensor_unit, "other"),
            levels_upper=("fixed", levels_upper) if levels_upper else ("no_levels", None),
            levels_lower=("fixed", levels_lower) if levels_lower else ("no_levels", None),
            render_func=lambda v: f"{v:.2f} {unit}",
        )
        yield Result(state=State(state), summary=infotext)


def check_oracle_ilom_temp(
    item: str, params: TempParamDict, section: Dict[str, ILOMSens]
) -> CheckResult:
    """check the state of a temperature sensor"""
    data = section.get(item)
    if data:
        state, state_readable = oracle_ilom_map_state.get(
            data.sensor_state, (3, "unknown")
        )
        perfdata = process_oracle_ilom_perfdata(data)

        yield from check_temperature(
            perfdata.value,
            params,
            unique_name=f"oracle_ilom_{item}",
            value_store=get_value_store(),
            dev_unit=data.sensor_unit,
            dev_levels=(
                perfdata.levels_upper[1]
                if perfdata.levels_upper and len(perfdata.levels_upper) > 1
                else None
            ),
            dev_levels_lower=(
                perfdata.levels_lower[1]
                if perfdata.levels_lower and len(perfdata.levels_lower) > 1
                else None
            ),
            dev_status=state,
            dev_status_name=state_readable,
        )


check_plugin_oracle_ilom_temp = CheckPlugin(
    name="oracle_ilom_temp",
    sections=["oracle_ilom"],
    service_name="Temperature %s",
    discovery_function=discover_oracle_ilom,
    discovery_default_parameters={"value": "temperature"},
    discovery_ruleset_name="inventory_oracle_ilom",
    check_function=check_oracle_ilom_temp,
    check_default_parameters={},
    check_ruleset_name="temperature",
)

check_plugin_oracle_ilom_fan = CheckPlugin(
    name="oracle_ilom_fan",
    sections=["oracle_ilom"],
    service_name="Fan %s",
    discovery_function=discover_oracle_ilom,
    discovery_default_parameters={"value": "tachometer"},
    discovery_ruleset_name="inventory_oracle_ilom",
    check_function=check_oracle_ilom,
    check_default_parameters={},
    check_ruleset_name="ilom_sensor",
)

check_plugin_oracle_ilom_voltage = CheckPlugin(
    name="oracle_ilom_voltage",
    sections=["oracle_ilom"],
    service_name="Voltage %s",
    discovery_function=discover_oracle_ilom,
    discovery_default_parameters={"value": "voltage"},
    discovery_ruleset_name="inventory_oracle_ilom",
    check_function=check_oracle_ilom,
    check_default_parameters={},
    check_ruleset_name="ilom_sensor",
)

check_plugin_oracle_ilom_other = CheckPlugin(
    name="oracle_ilom_other",
    sections=["oracle_ilom"],
    service_name="Other %s",
    discovery_function=discover_oracle_ilom,
    discovery_default_parameters={"value": "other"},
    discovery_ruleset_name="inventory_oracle_ilom",
    check_function=check_oracle_ilom,
    check_default_parameters={},
    check_ruleset_name="ilom_sensor",
)

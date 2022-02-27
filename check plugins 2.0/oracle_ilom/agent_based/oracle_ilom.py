#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

from typing import Dict, NamedTuple, List
from .agent_based_api.v1 import (
    register,
    Result,
    Service,
    SNMPTree,
    State,
    contains,
    OIDEnd,
    check_levels,
    get_value_store,
)
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, StringTable
from .utils.temperature import check_temperature, TempParamDict

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


class ILOMSens(NamedTuple):
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


Section = Dict[str, ILOMSens]


def parse_oracle_ilom(string_table: List[StringTable]) -> Section:
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
        sensor_bit_mask,
    ) in sensors:
        sensor_name = "Sensor %s %s" % (sensor_id, entities[sensor_id]["name"].strip())
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


register.snmp_section(
    name="oracle_ilom",
    parse_function=parse_oracle_ilom,
    detect=contains(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.42.2.200"),
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.42.2.70.101.1.1.8.1",
            oids=[
                OIDEnd(),
                "1",   # sunPlatNumericSensorBaseUnits
                "2",   # sunPlatNumericSensorExponent
                "4",   # sunPlatNumericSensorCurrent
                "8",   # sunPlatNumericSensorLowerThresholdNonCritical
                "9",   # sunPlatNumericSensorUpperThresholdNonCritical
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


def discover_oracle_ilom(params, section: Dict[str, ILOMSens]) -> DiscoveryResult:
    for key, values in section.items():
        if values.availability == "2" and values.sensor_type == params.get("value"):
            yield Service(item=key, parameters={})


def check_oracle_ilom(item: str, section: Dict[str, ILOMSens]) -> CheckResult:
    data = section.get(item)
    if data:
        state, state_readable = oracle_ilom_map_state.get(
            data.sensor_state, (3, "unknown")
        )
        unit = data.sensor_unit
        precision = pow(10, int(data.sensor_exponent))
        reading = int(data.sensor_value_str) * precision
        crit_lower = (
            int(data.sensor_lower_crit_value) * precision
            if int(data.sensor_lower_crit_value) != 0
            else None
        )
        warn_lower = (
            int(data.sensor_lower_warn_value) * precision
            if int(data.sensor_lower_warn_value) != 0
            else None
        )
        crit = (
            int(data.sensor_upper_crit_value) * precision
            if int(data.sensor_upper_crit_value) != 0
            else None
        )
        warn = (
            int(data.sensor_upper_warn_value) * precision
            if int(data.sensor_upper_warn_value) != 0
            else None
        )
        infotext = "status: %s" % (state_readable)
        yield from check_levels(
            reading,
            metric_name=oracle_ilom_unit_perf.get(data.sensor_unit, "other"),
            levels_upper=(warn, crit),
            levels_lower=(warn_lower, crit_lower),
            render_func=lambda value: "%.2f %s" % (value, unit),
        )
        yield Result(state=State(state), summary=infotext)


def check_oracle_ilom_temp(
    item: str, params: TempParamDict, section: Dict[str, ILOMSens]
) -> CheckResult:
    data = section.get(item)
    if data:
        state, state_readable = oracle_ilom_map_state.get(
            data.sensor_state, (3, "unknown")
        )
        precision = pow(10, int(data.sensor_exponent))
        reading = int(data.sensor_value_str) * precision
        crit_lower = (
            int(data.sensor_lower_fatal_value) * precision
            if int(data.sensor_lower_fatal_value) != 0
            else None
        )
        warn_lower = (
            int(data.sensor_lower_warn_value) * precision
            if int(data.sensor_lower_warn_value) != 0
            else None
        )
        crit = (
            int(data.sensor_upper_fatal_value) * precision
            if int(data.sensor_upper_fatal_value) != 0
            else None
        )
        warn = (
            int(data.sensor_upper_warn_value) * precision
            if int(data.sensor_upper_warn_value) != 0
            else None
        )

        yield from check_temperature(
            reading,
            params,
            unique_name="oracle_ilom_%s" % item,
            value_store=get_value_store(),
            dev_unit=data.sensor_unit,
            dev_levels=(warn, crit),
            dev_levels_lower=(warn_lower, crit_lower),
            dev_status=state,
            dev_status_name=state_readable,
        )


register.check_plugin(
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

register.check_plugin(
    name="oracle_ilom_fan",
    sections=["oracle_ilom"],
    service_name="Fan %s",
    discovery_function=discover_oracle_ilom,
    discovery_default_parameters={"value": "tachometer"},
    discovery_ruleset_name="inventory_oracle_ilom",
    check_function=check_oracle_ilom,
)

register.check_plugin(
    name="oracle_ilom_voltage",
    sections=["oracle_ilom"],
    service_name="Voltage %s",
    discovery_function=discover_oracle_ilom,
    discovery_default_parameters={"value": "voltage"},
    discovery_ruleset_name="inventory_oracle_ilom",
    check_function=check_oracle_ilom,
)

register.check_plugin(
    name="oracle_ilom_other",
    sections=["oracle_ilom"],
    service_name="Other %s",
    discovery_function=discover_oracle_ilom,
    discovery_default_parameters={"value": "other"},
    discovery_ruleset_name="inventory_oracle_ilom",
    check_function=check_oracle_ilom,
)

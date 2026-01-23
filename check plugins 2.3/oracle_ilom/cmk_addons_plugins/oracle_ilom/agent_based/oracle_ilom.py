#!/usr/bin/env python3
"""Oracle ILOM sensor and problem checks"""
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from typing import Any, Dict, List, NamedTuple

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
from cmk_addons.plugins.oracle_ilom.lib import (
    process_oracle_ilom_perfdata,
    convert_date_and_time,
)
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

oracle_ilom_map_subsystem = {
    "1": "None",
    "2": "Cooling",
    "3": "Processors",
    "4": "Memory",
    "5": "Power",
    "6": "Storage",
    "7": "Network",
    "8": "IOModule",
    "9": "Blade",
    "10": "DCU",
    "11": "CPUModule",
    "12": "PCIDevices",
    "13": "ORD",
    "99": "Unknown",
}

# Subsystems to create dedicated checks for
DEDICATED_SUBSYSTEMS = {
    "3": "Processors",
    "4": "Memory",
    "5": "Power",
    "2": "Cooling",
    "6": "Storage",
    "7": "Network",
}

# Reverse mapping for subsystem name to code
SUBSYSTEM_NAME_TO_CODE = {v: k for k, v in DEDICATED_SUBSYSTEMS.items()}
SUBSYSTEM_NAME_TO_CODE["Others"] = "others"

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


Section = Dict[str, Any]


def parse_oracle_ilom(string_table: List[StringTable]) -> Section:
    """parse data into dictionary"""
    parsed = {}
    entities = {}
    sensors, entity, types, problems_count, problems_table = string_table

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

    # Parse open problems count
    if problems_count:
        parsed["open_problems_count"] = int(problems_count[0][0])

    # Parse open problems
    problems_by_subsystem = {}
    for entry in problems_table:
        if len(entry) >= 5:
            index, timestamp, subsystem, location, description = entry[:5]
            if subsystem not in problems_by_subsystem:
                problems_by_subsystem[subsystem] = []
            problems_by_subsystem[subsystem].append({
                'timestamp': convert_date_and_time(timestamp),
                'location': location,
                'description': description,
            })
    parsed["open_problems"] = problems_by_subsystem

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
                "2",  # sunPlatSensorType
            ],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.42.2.2.6.4.1.1",
            oids=[
                "2.0",  # ilomSystemOpenProblemsCount
            ],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.42.2.2.6.4.1.1.10.1",
            oids=[
                OIDEnd(),
                "2",  # ilomSystemOpenProblemTimestamp
                "3",  # ilomSystemOpenProblemSubsystem
                "4",  # ilomSystemOpenProblemLocation
                "5",  # ilomSystemOpenProblemDescription
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


def discover_oracle_ilom(params, section: Section) -> DiscoveryResult:
    """for every sensor one service is discovered"""
    for key, values in section.items():
        if isinstance(values, ILOMSens) and values.availability == "2" and values.sensor_type == params.get("value"):
            yield Service(item=key, parameters={})


def check_oracle_ilom(
    item: str, params: IlomParamDict, section: Section
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
    item: str, params: TempParamDict, section: Section
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


def discover_oracle_ilom_processors_status(section: Section) -> DiscoveryResult:
    """Discover Processors status service"""
    if "open_problems_count" in section:
        yield Service(item="Subsystem Processors Status")


def discover_oracle_ilom_memory_status(section: Section) -> DiscoveryResult:
    """Discover Memory status service"""
    if "open_problems_count" in section:
        yield Service(item="Subsystem Memory Status")


def discover_oracle_ilom_power_status(section: Section) -> DiscoveryResult:
    """Discover Power status service"""
    if "open_problems_count" in section:
        yield Service(item="Subsystem Power Status")


def discover_oracle_ilom_cooling_status(section: Section) -> DiscoveryResult:
    """Discover Cooling status service"""
    if "open_problems_count" in section:
        yield Service(item="Subsystem Cooling Status")


def discover_oracle_ilom_storage_status(section: Section) -> DiscoveryResult:
    """Discover Storage status service"""
    if "open_problems_count" in section:
        yield Service(item="Subsystem Storage Status")


def discover_oracle_ilom_network_status(section: Section) -> DiscoveryResult:
    """Discover Network status service"""
    if "open_problems_count" in section:
        yield Service(item="Subsystem Network Status")


def discover_oracle_ilom_others_status(section: Section) -> DiscoveryResult:
    """Discover Others status service"""
    if "open_problems_count" in section:
        yield Service(item="Subsystem Others Status")


def check_oracle_ilom_status(
    item: str, section: Section
) -> CheckResult:
    """Check status of a specific subsystem"""
    open_problems = section.get("open_problems", {})
    
    # Extract subsystem name from item (e.g., "Subsystem Processors Status" -> "Processors")
    subsystem_name = item.replace("Subsystem ", "").replace(" Status", "")
    
    if subsystem_name == "Others":
        # Others contains all non-dedicated subsystems
        subsystems_to_check = {
            code: open_problems.get(code, [])
            for code in open_problems.keys()
            if code not in DEDICATED_SUBSYSTEMS
        }
    else:
        # Dedicated subsystem
        subsystem_code = SUBSYSTEM_NAME_TO_CODE.get(subsystem_name)
        if not subsystem_code:
            yield Result(state=State.UNKNOWN, summary=f"Unknown subsystem: {subsystem_name}")
            return
        subsystems_to_check = {
            subsystem_code: open_problems.get(subsystem_code, [])
        }
    
    # Count total problems in this subsystem(s)
    total_problems = sum(len(problems) for problems in subsystems_to_check.values())
    
    if total_problems > 0:
        summary_parts = []
        details = ""
        
        for subsystem_code, problems in subsystems_to_check.items():
            if problems:
                subsys_name = oracle_ilom_map_subsystem.get(subsystem_code, f"Subsystem {subsystem_code}")
                summary_parts.append(f"{subsys_name}: {len(problems)}")
                details += f"[{subsys_name}]:\n"
                for problem in problems:
                    details += f"{problem['timestamp']} - {problem['location']} - {problem['description']}\n"
        
        summary = ", ".join(summary_parts) if summary_parts else ""
        yield Result(
            state=State.CRIT,
            summary=f"Open problems: {total_problems}" + (f" ({summary})" if summary else ""),
            details=details.strip()
        )
    else:
        yield Result(state=State.OK, summary=f"OK - No open problem")


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

check_plugin_oracle_ilom_processors_status = CheckPlugin(
    name="oracle_ilom_processors_status",
    sections=["oracle_ilom"],
    service_name="%s",
    discovery_function=discover_oracle_ilom_processors_status,
    check_function=check_oracle_ilom_status,
)

check_plugin_oracle_ilom_memory_status = CheckPlugin(
    name="oracle_ilom_memory_status",
    sections=["oracle_ilom"],
    service_name="%s",
    discovery_function=discover_oracle_ilom_memory_status,
    check_function=check_oracle_ilom_status,
)

check_plugin_oracle_ilom_power_status = CheckPlugin(
    name="oracle_ilom_power_status",
    sections=["oracle_ilom"],
    service_name="%s",
    discovery_function=discover_oracle_ilom_power_status,
    check_function=check_oracle_ilom_status,
)

check_plugin_oracle_ilom_cooling_status = CheckPlugin(
    name="oracle_ilom_cooling_status",
    sections=["oracle_ilom"],
    service_name="%s",
    discovery_function=discover_oracle_ilom_cooling_status,
    check_function=check_oracle_ilom_status,
)

check_plugin_oracle_ilom_storage_status = CheckPlugin(
    name="oracle_ilom_storage_status",
    sections=["oracle_ilom"],
    service_name="%s",
    discovery_function=discover_oracle_ilom_storage_status,
    check_function=check_oracle_ilom_status,
)

check_plugin_oracle_ilom_network_status = CheckPlugin(
    name="oracle_ilom_network_status",
    sections=["oracle_ilom"],
    service_name="%s",
    discovery_function=discover_oracle_ilom_network_status,
    check_function=check_oracle_ilom_status,
)

check_plugin_oracle_ilom_others_status = CheckPlugin(
    name="oracle_ilom_others_status",
    sections=["oracle_ilom"],
    service_name="%s",
    discovery_function=discover_oracle_ilom_others_status,
    check_function=check_oracle_ilom_status,
)

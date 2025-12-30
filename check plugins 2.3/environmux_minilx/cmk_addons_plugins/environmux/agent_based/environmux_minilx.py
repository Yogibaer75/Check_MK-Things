#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping
from dataclasses import dataclass
from cmk.agent_based.v2 import CheckPlugin, SimpleSNMPSection, SNMPTree, startswith, StringTable
from cmk.plugins.lib.enviromux import (
    check_enviromux_humidity,
    check_enviromux_temperature,
    discover_enviromux_humidity,
    discover_enviromux_temperature,
    SENSOR_TYPE_NAMES,
)

DETECT_ENVIROMUX_MINILX = startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.3699.1.1.8")

@dataclass
class EnviromuxSensor:
    type_: str
    value: float
    min_threshold: float | None = None  # This is not present for the EnviromuxMicro devices
    max_threshold: float | None = None  # This is not present for the EnviromuxMicro devices


@dataclass
class EnviromuxDigitalSensor:
    value: str
    normal_value: str


@dataclass
class EnviromuxMicroSensor:
    type_: str
    value: float


EnviromuxDigitalSection = Mapping[str, EnviromuxDigitalSensor]
EnviromuxSection = Mapping[str, EnviromuxSensor]


def parse_enviromux_minilx(
    string_table: StringTable,
) -> EnviromuxSection:
    enviromux_minilx_sensors: dict[str, EnviromuxSensor] = {}

    for line in string_table:
        try:
            if line[1] == "32770":
                value = float(line[3])
            else:
                value = float(line[3]) / 10.0

            enviromux_minilx_sensors.setdefault(
                f"{line[2]} {line[0]}" if "#" not in line[2] else line[2],
                EnviromuxSensor(
                    type_=SENSOR_TYPE_NAMES.get(line[1], "Unknown"),
                    value=value,
                ),
            )
        except (IndexError, ValueError):
            continue

    return enviromux_minilx_sensors


snmp_section_enviromux_minilx = SimpleSNMPSection(
    name="enviromux_minilx",
    parse_function=parse_enviromux_minilx,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.3699.1.1.8.1.5.1.1",
        oids=[
            "1",  # intSensorIndex
            "2",  # intSensorType
            "3",  # intSensorDescription
            "7",  # intSensorValue
        ],
    ),
    detect=DETECT_ENVIROMUX_MINILX,
)

# .
#   .--temperature---------------------------------------------------------.
#   |      _                                      _                        |
#   |     | |_ ___ _ __ ___  _ __   ___ _ __ __ _| |_ _   _ _ __ ___       |
#   |     | __/ _ \ '_ ` _ \| '_ \ / _ \ '__/ _` | __| | | | '__/ _ \      |
#   |     | ||  __/ | | | | | |_) |  __/ | | (_| | |_| |_| | | |  __/      |
#   |      \__\___|_| |_| |_| .__/ \___|_|  \__,_|\__|\__,_|_|  \___|      |
#   |                       |_|                                            |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'


check_plugin_enviromux_minilx_temperature = CheckPlugin(
    name="enviromux_minilx_temperature",
    sections=["enviromux_minilx"],
    discovery_function=discover_enviromux_temperature,
    check_function=check_enviromux_temperature,
    service_name="Sensor %s",
    check_default_parameters={},
    check_ruleset_name="temperature",
)

# .
#   .--Humidity------------------------------------------------------------.
#   |              _   _                 _     _ _ _                       |
#   |             | | | |_   _ _ __ ___ (_) __| (_) |_ _   _               |
#   |             | |_| | | | | '_ ` _ \| |/ _` | | __| | | |              |
#   |             |  _  | |_| | | | | | | | (_| | | |_| |_| |              |
#   |             |_| |_|\__,_|_| |_| |_|_|\__,_|_|\__|\__, |              |
#   |                                                  |___/               |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'

check_plugin_enviromux_minilx_humidity = CheckPlugin(
    name="enviromux_minilx_humidity",
    sections=["enviromux_minilx"],
    service_name="Sensor %s",
    discovery_function=discover_enviromux_humidity,
    check_function=check_enviromux_humidity,
    check_default_parameters={},
    check_ruleset_name="humidity",
)
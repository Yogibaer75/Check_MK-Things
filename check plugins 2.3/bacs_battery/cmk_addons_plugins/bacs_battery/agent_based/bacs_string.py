#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
"""check for BACS battery string status"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from typing import Any, Mapping

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    State,
    StringTable,
    check_levels,
    startswith,
)

bacs_string_default_levels = {
    "voltage": ("fixed", (440, 445)),
    "voltage_lower": ("fixed", (435, 430)),
    "temp": ("fixed", (40, 50)),
    "temp_lower": ("fixed", (10, 5)),
    "resistance": ("fixed", (15, 18)),
}

Section = Mapping[str, Any]


def parse_bacs_string(string_table: StringTable) -> Section:
    """parse data to dict"""
    scale = 100.0
    parsed = {}
    for i in string_table:
        parsed[i[0]] = {
            "power": int(i[1]) / scale,
            "overall": int(i[2]) / scale,
            "average": int(i[3]) / scale,
        }
    return parsed


snmp_section_bacs_string = SimpleSNMPSection(
    name="bacs_string",
    detect=startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.2.1.33"),
    parse_function=parse_bacs_string,
    fetch=SNMPTree(
        base=".1.3.6.1.2.1.33.5.2.7.1",
        oids=[
            "1",  # string index
            "2",  # string power
            "3",  # string overall voltage
            "4",  # string average voltage
        ],
    ),
)


def inventory_bacs_string(section: Section) -> DiscoveryResult:
    """one service is discovered per string"""
    for item in section:
        yield Service(item=item)


def check_bacs_string(item: str, params, section: Section) -> CheckResult:
    """check status of a single string"""
    data = section.get(item)
    if not data:
        return

    average = data.get("average", 0)
    yield Result(
        state=State(0),
        summary=f"String {item}, Average Voltage: {average}",
    )
    yield from check_levels(
        float(data.get("overall", 0)),
        levels_upper=params.get("voltage", ("no_levels", None)),
        levels_lower=params.get("voltage_lower", ("no_levels", None)),
        metric_name="voltage",
        label="Overall Voltage",
        render_func=lambda v: f"{v:.2f}V",
    )
    yield from check_levels(
        float(data.get("power", 0)),
        levels_upper=(0.01, 0.01),
        metric_name="power",
        label="Battery Power",
        render_func=lambda v: f"{v:.2f}A",
    )
    yield Metric("avg_volt", float(average))


check_plugin_bacs_string = CheckPlugin(
    name="bacs_string",
    check_function=check_bacs_string,
    discovery_function=inventory_bacs_string,
    service_name="BACS String %s",
    check_default_parameters=bacs_string_default_levels,
    check_ruleset_name="bacs",
)

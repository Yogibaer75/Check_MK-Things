#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
"""check for BACS battery string status"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from typing import Mapping, Any
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    startswith,
    register,
    Metric,
    Result,
    Service,
    SNMPTree,
    State,
    check_levels,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
    StringTable,
)

bacs_string_default_levels = {
    "levels": (55, 60),
    "voltage": (440, 445),
    "voltage_lower": (435, 430),
    "temp": (40, 50),
    "temp_lower": (10, 5),
    "resistance": (15, 18),
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


register.snmp_section(
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
        levels_upper=params["voltage"],
        levels_lower=params["voltage_lower"],
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


register.check_plugin(
    name="bacs_string",
    check_function=check_bacs_string,
    discovery_function=inventory_bacs_string,
    service_name="BACS String %s",
    check_default_parameters=bacs_string_default_levels,
    check_ruleset_name="bacs",
)

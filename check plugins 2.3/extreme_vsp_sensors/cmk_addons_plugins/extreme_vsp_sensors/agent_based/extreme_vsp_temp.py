#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Mapping, NamedTuple

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    get_value_store,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    StringTable,
    all_of,
    startswith,
)
from cmk.plugins.lib.netextreme import DETECT_NETEXTREME
from cmk.plugins.lib.temperature import TempParamDict, check_temperature

DETECT_VSP = all_of(
    startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1916.2.325"),
    startswith(".1.3.6.1.2.1.1.1.0", "VSP-74"),
)


class TEMP(NamedTuple):
    """Temperature sensor data structure."""
    value: int
    warn: int
    crit: int
    state: int


Section = Mapping[str, TEMP]


def parse_extreme_vsp_temp(string_table: StringTable) -> Section:
    """
    >>> parse_extreme_vsp_temp([["Sensor1", "30", "40", "50", "1"]])
    {'Sensor1': TEMP(value=30, warn=40, crit=50, state=1)}
    """
    return {
        f"{entry[0]}": TEMP(
            value=int(entry[1]),
            warn=int(entry[2]),
            crit=int(entry[3]),
            state=int(entry[4]),
        )
        for entry in string_table
    }


snmp_section_extreme_vsp_temp = SimpleSNMPSection(
    name="extreme_vsp_temp",
    detect=DETECT_NETEXTREME,
    parse_function=parse_extreme_vsp_temp,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.2272.1.101.1.1.2.1",
        oids=[
            "2",  # name
            "3",  # value
            "4",  # warn
            "5",  # crit
            "6",  # status
        ],
    ),
)


def discover_extreme_vsp_temp(section: Section) -> DiscoveryResult:
    """One service per temperature sensor."""
    for item, _entry in section.items():
        yield Service(item=item)


def check_extreme_vsp_temp(
    item: str, params: TempParamDict, section: Section
) -> CheckResult:
    temp = section.get(item)
    if not temp:
        return

    warn = temp.warn
    crit = temp.crit
    if warn == 0 and crit != 0:
        warn = crit
    if crit == 0 and warn != 0:
        crit = warn

    yield from check_temperature(
        temp.value,
        params,
        unique_name=item,
        value_store=get_value_store(),
        dev_levels=(warn, crit),
    )


check_plugin_extreme_vsp_temp = CheckPlugin(
    name="extreme_vsp_temp",
    service_name="Temperature %s",
    discovery_function=discover_extreme_vsp_temp,
    check_function=check_extreme_vsp_temp,
    check_default_parameters={},
    check_ruleset_name="temperature",
)

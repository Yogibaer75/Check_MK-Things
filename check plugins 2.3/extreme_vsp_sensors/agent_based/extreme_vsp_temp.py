#!/usr/bin/env python3
"""Extreme VPS temperature checks"""
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from typing import Mapping, NamedTuple
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    all_of,
    startswith,
    register,
    Service,
    SNMPTree,
    get_value_store,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
    StringTable,
)
from cmk.base.plugins.agent_based.utils.temperature import (
    check_temperature,
    TempParamDict,
)

DETECT_VSP = all_of(
    startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1916.2.325"),
    startswith(".1.3.6.1.2.1.1.1.0", "VSP-74"),
)


class TEMP(NamedTuple):
    '''temperature named tuple'''
    value: int
    warn: int
    crit: int
    state: int


Section = Mapping[str, TEMP]


def parse_extreme_vsp_temp(string_table: StringTable) -> Section:
    '''parse data into dictionary'''
    return {
        f"{entry[0]}": TEMP(
            value=int(entry[1]),
            warn=int(entry[2]),
            crit=int(entry[3]),
            state=int(entry[4]),
        )
        for entry in string_table
    }


register.snmp_section(
    name="extreme_vsp_temp",
    detect=DETECT_VSP,
    parse_function=parse_extreme_vsp_temp,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.2272.1.101.1.1.2.1",
        oids=[
            "2",
            "3",
            "4",
            "5",
            "6",
        ],  # name  # value  # warn  # crit  # status
    ),
)


def discover_extreme_vsp_temp(section: Section) -> DiscoveryResult:
    '''for every sensor a service is discovered'''
    for item, _entry in section.items():
        yield Service(item=item)


def check_extreme_vsp_temp(
    item: str, params: TempParamDict, section: Section
) -> CheckResult:
    '''check the status of a single sensor'''
    temp = section.get(item)
    if not temp:
        return

    yield from check_temperature(
        temp.value,
        params,
        unique_name=item,
        value_store=get_value_store(),
        dev_levels=(temp.warn, temp.crit),
    )


register.check_plugin(
    name="extreme_vsp_temp",
    service_name="Temperature %s",
    discovery_function=discover_extreme_vsp_temp,
    check_function=check_extreme_vsp_temp,
    check_default_parameters={},
    check_ruleset_name="temperature",
)

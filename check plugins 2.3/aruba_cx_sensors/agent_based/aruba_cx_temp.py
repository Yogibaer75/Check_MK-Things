#!/usr/bin/env python3
"""check for temperature status of Aruba CX 6k switches"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from typing import Optional, Dict, Any
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    DiscoveryResult,
    CheckResult,
    StringTable,
)
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    get_value_store,
    register,
    Result,
    Service,
    SNMPTree,
    State,
    OIDEnd,
)
from cmk.base.plugins.agent_based.utils.temperature import (
    check_temperature,
    TempParamDict,
)
from .utils.aruba_cx import DETECT_ARUBA_CX

Section = Dict[str, Any]


def parse_arbua_cx_temp(string_table: StringTable) -> Optional[Section]:
    """parse raw snmp data to dictionary"""
    try:
        parsed = {}
        for line in string_table:
            parsed.setdefault(
                line[1], {"state": line[2], "temp": float(line[3]) / 1000}
            )
        return parsed
    except IndexError:
        return {}


def discovery_arbua_cx_temp(section: Section) -> DiscoveryResult:
    """every key of the parsed data is found as a service"""
    for key in section.keys():
        yield Service(item=key)


def check_arbua_cx_temp(item, params: TempParamDict, section: Section) -> CheckResult:
    """check the temperature of the sensor"""
    data = section.get(item)
    if not data:
        return

    yield from check_temperature(
        reading=data.get("temp", 0),
        params=params,
        unique_name=item,
        value_store=get_value_store(),
    )
    if data.get("state") != "normal":
        yield Result(
            state=State.WARN, summary=f"Status not normal --> {data.get('state')}"
        )


register.snmp_section(
    name="arbua_cx_temp",
    parse_function=parse_arbua_cx_temp,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.47196.4.1.1.3.11.3.1.1",
        oids=[
            OIDEnd(),
            "5",
            "6",
            "7",
        ],
    ),
    detect=DETECT_ARUBA_CX,
)

register.check_plugin(
    name="arbua_cx_temp",
    service_name="Temperature %s",
    discovery_function=discovery_arbua_cx_temp,
    check_function=check_arbua_cx_temp,
    check_default_parameters={},
    check_ruleset_name="temperature",
)

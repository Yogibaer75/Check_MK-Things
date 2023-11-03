#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Matthias Binder 'hds@kpc.de' - K&P Computer Service- und Vertriebs-GmbH
# (c) Andreas Doehler 'andreas.doehler@bechtle.com'
# License: GNU General Public License v2

from typing import Any, Dict, Optional
from datetime import datetime
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    all_of,
    check_levels,
    exists,
    register,
    startswith,
    Result,
    Service,
    SNMPTree,
    State,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
    StringTable,
)

Section = Dict[str, Dict[str, str]]


def parse_sophosxg_lic(string_table: StringTable) -> Optional[Section]:
    """parse raw snmp data to dictionary"""
    lic_table: list[str] = [
        "Base FW",
        "Net Protection",
        "Web Protection",
        "Mail Protection",
        "Web Server Protection",
        "Sandstorm",
        "Enhanced Support",
        "Enhanced Plus",
        "Central Orchestration",
    ]
    try:
        parsed = {}
        for x in range(8):
            parsed.setdefault(
                lic_table[x], {"state": string_table[0][x],
                               "date": string_table[1][x]}
            )
        return parsed
    except IndexError:
        return {}


register.snmp_section(
    name="sophosxg_lic",
    parse_function=parse_sophosxg_lic,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.2604.5.1.5",
        oids=[
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
        ],
    ),
    detect=all_of(
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.2604.5"),
        exists(".1.3.6.1.4.1.2604.5.1.1.*"),
    ),
)


def discover_sophosxg_lic(section: Section) -> DiscoveryResult:
    """every key of the parsed data is creating one service"""
    for key in section.keys():
        yield Service(item=key)


def check_sophosxg_lic(item: str, params: Dict[str, Any], section: Section) -> CheckResult:
    """check the license state of single items"""
    data = section.get(item)
    if not data:
        return

    lic_state: Dict[str, tuple[str, int]] = {
        "0": ("none", 1),
        "1": ("evaluating", 1),
        "2": ("not subscribed", 1),
        "3": ("subscribed", 0),
        "4": ("expired", 2),
        "5": ("deactivated", 0),
        "99": ("unknown", 3),
    }

    warn, crit = params.get("levels", (40, 30))
    wanted_state = params.get("state", "99")

    lictext, licstate = lic_state.get(data.get("state", "99"), ("unknown", 3))
    licexpire = data.get("date", "unknown")

    try:
        date = datetime.strptime(licexpire, "%b %d %Y")
        days_left = (date - datetime.now()).days
    except ValueError:
        days_left = 9999999

    if data.get("state") == wanted_state:
        yield Result(state=State.OK, summary=f"Current state is {lictext}")
    else:
        if wanted_state != "99":
            yield Result(
                state=State(licstate),
                summary=f"Current state is {lictext} - wanted state was \
                          {lic_state.get(wanted_state,('unknown', 3))[0]}",
            )
        else:
            yield Result(
                state=State.OK,
                summary=f"Current state is {lictext} - no preference selected",
            )

    if days_left < 9999999 and data.get("state") in ["1", "3"]:
        yield from check_levels(
            value=days_left,
            levels_lower=(warn, crit),
            metric_name="days",
            label="Days left",
            render_func=lambda x: f"{x:0.0f}",
        )


register.check_plugin(
    name="sophosxg_lic",
    service_name="License %s",
    discovery_function=discover_sophosxg_lic,
    check_function=check_sophosxg_lic,
    check_default_parameters={
        "levels": (40, 30),
        "state": "3",
    },
    check_ruleset_name="sophosxg_lic",
)

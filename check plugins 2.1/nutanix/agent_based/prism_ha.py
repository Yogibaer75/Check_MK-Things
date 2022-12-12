#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

import ast
import time
from typing import Any, Dict, Mapping

from .agent_based_api.v1 import register, Result, Service, State
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, StringTable

Section = Dict[str, Mapping[str, Any]]


def parse_prism_ha(string_table: StringTable) -> Section:
    data = ast.literal_eval(string_table[0][0])

    return data


register.agent_section(
    name="prism_ha",
    parse_function=parse_prism_ha,
)

def discovery_prism_ha(section: Section) -> DiscoveryResult:
    yield Service()

def check_prism_ha(section: Section) -> CheckResult:
    if section["failover_enabled"]:
        if section["ha_state"] == "HighlyAvailable":
            state=State.OK
        else:
            state=State.CRIT
    else:
        state=State.OK

    yield Result(state=state, summary=f"State: {section['ha_state']}")

register.check_plugin(
    name="prism_ha",
    service_name="NTNX High Availability",
    sections=["prism_ha"],
    discovery_function=discovery_prism_ha,
    check_function=check_prism_ha,
)
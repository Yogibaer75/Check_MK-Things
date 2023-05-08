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

# <<<ilo_api_general:sep(124)>>>
# ProLiant DL380 Gen10|U30 v2.04 (04/18/2019)|CZ123456789|OK
# Server Typ | BIOS Ver. | Serial | Health

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)

from .agent_based_api.v1 import (
    register,
    Result,
    State,
    Service,
)

from .utils.hp_ilo import parse_hp_ilo

register.agent_section(
    name="ilo_api_general",
    parse_function=parse_hp_ilo,
)


def discovery_ilo_api_general(section) -> DiscoveryResult:
    for element in section:
        yield Service(item=element)


def check_ilo_api_general(item: str, section) -> CheckResult:
    data = section.get(item)
    if data:
        if data[3] == "OK":
            yield Result(
                state=State(0),
                summary="Operational state OK - BIOS %s -  Serial %s" %
                (data[1].replace("_", " "), data[2]))
        elif data[3] == "Warning":
            yield Result(
                state=State(1),
                summary="Operational state Warning - BIOS %s -  Serial %s" %
                (data[1].replace("_", " "), data[2]))
        else:
            yield Result(state=State(2),
                         summary="Error in System with Status %s" % data[3])


register.check_plugin(
    name="ilo_api_general",
    service_name="General Status %s",
    sections=["ilo_api_general"],
    discovery_function=discovery_ilo_api_general,
    check_function=check_ilo_api_general,
)

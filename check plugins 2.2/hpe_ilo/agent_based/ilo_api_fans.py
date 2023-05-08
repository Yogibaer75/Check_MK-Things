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

# <<<ilo_api_fans:sep(124)>>>
# Fan 1|11|Percent|Enabled|OK
# Name | Speed | Unit | Status | Health

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)

from .agent_based_api.v1 import (
    register,
    Result,
    State,
    Service,
    Metric,
)

from .utils.hp_ilo import parse_hp_ilo

register.agent_section(
    name="ilo_api_fans",
    parse_function=parse_hp_ilo,
)


def discovery_ilo_api_fans(section) -> DiscoveryResult:
    for element in section:
        if (section[element][3] != "Absent"):
            yield Service(item=element)


def check_ilo_api_fans(item: str, section) -> CheckResult:
    data = section.get(item)
    if data:
        if len(data[1]) != 0:
            perc = int(data[1])
        else:
            perc = "undef"

        if data[4] == "OK" and perc != "undef":
            yield Result(state=State(0),
                         summary="Operational state OK - %s%% Speed" % perc)
            yield Metric("perc", perc, boundaries=(0, 100))
        elif data[4] == "OK":
            yield Result(state=State(0), summary="Operational state OK")
        else:
            yield Result(state=State(2), summary="Error in %s" % item)


register.check_plugin(
    name="ilo_api_fans",
    service_name="HW %s",
    sections=["ilo_api_fans"],
    discovery_function=discovery_ilo_api_fans,
    check_function=check_ilo_api_fans,
)

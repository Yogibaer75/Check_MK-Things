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

# Example Output:
# <<<win_cert:sep(58):cached(1480065612,90000)>>>
#
# Subject  : CN=SUPERSERVER1, DC=group, DC=de
# Issuer   : O=COMPANY, OU=IT, DC=COMPANY, DC=group, DC=de
# NotAfter : 31.01.2017 15:49:44
#
# Subject  : CN=SUPERSERVER2, DC=group, DC=de
# Issuer   : O=COMPANY, OU=IT, DC=COMPANY, DC=group, DC=de
# NotAfter : 11.01.2017 15:17:35

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)

from .agent_based_api.v1 import (
    check_levels,
    register,
    render,
    Result,
    State,
    Service,
)

import datetime as dt


def parse_win_cert(string_table):
    parsed = {}
    last_cert = False
    for line in string_table:
        key = line[0].strip()
        val = ":".join(line[1:]).strip()
        if last_cert and key != "Subject":
            parsed[last_cert][key] = val
        if key == "Subject":
            last_cert = val
            parsed[last_cert] = {}
    return parsed


register.agent_section(
    name="win_cert",
    parse_function=parse_win_cert,
)


def discovery_win_cert(section) -> DiscoveryResult:
    yield Service(item="Certificates")


def check_win_cert(item, params, section) -> CheckResult:
    warn, crit = params.get("levels")
    filter_issuer = params.get("issuer", [])
    for item in section:
        data = section[item]
        if data.get("Issuer") in filter_issuer:
            continue
        date = data.get("NotAfter")
        failed = False
        try:
            date_obj = dt.datetime.strptime(date, '%d.%m.%Y %H:%M:%S')
        except ValueError:
            failed = True
        if failed:
            try:
                date_obj = dt.datetime.strptime(date, '%m/%d/%Y %I:%M:%S %p')
                failed = False
            except ValueError:
                failed = True
        if failed:
            days_left = dt.datetime.now() - dt.datetime.now()
        else:
            days_left = date_obj - dt.datetime.now()

        yield Result(state=State.OK,
                     summary="Certificate %s is going to run out at %s in" %
                     (item, date))

        yield from check_levels(int(days_left.days) * 86400,
                                levels_lower=(warn * 86400, crit * 86400),
                                render_func=render.timespan)
    if len(section) == 0:
        yield Result(state=State.OK, summary="No Certificates found to run out")


register.check_plugin(
    name="win_cert",
    service_name="Windows %s",
    sections=["win_cert"],
    discovery_function=discovery_win_cert,
    check_function=check_win_cert,
    check_default_parameters={
        "levels": (30, 15),
    },
    check_ruleset_name="win_cert",
)

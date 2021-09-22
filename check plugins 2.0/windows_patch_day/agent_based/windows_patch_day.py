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

# Sample agent output
# <<<windows_patch_day:sep(124)>>>
# 2021-09 Kumulatives Update für Windows 10 Version 21H1 für x64-basierte Systeme (KB5005565)|09/17/2021 05:09:24|2
# 2021-09 .NET Core 3.1.19 Update for x64 Client (KB5006191)|09/16/2021 21:14:56|2
# Name | Install Date | Install State

import datetime
from typing import List, NamedTuple, Mapping, Any

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
    StringTable,
)

from .agent_based_api.v1 import (
    register,
    Result,
    State,
    Service,
)


class WinPatchday(NamedTuple):
    name: str
    date: str
    result: str


Section = List[WinPatchday]


def parse_windows_patch_day(string_table: StringTable) -> Section:
    return [
        WinPatchday(name, date, result) for name, date, result in string_table
    ]


register.agent_section(
    name="windows_patch_day",
    parse_function=parse_windows_patch_day,
)


def discovery_windows_patch_day(section: Section) -> DiscoveryResult:
    yield Service()


def check_windows_patch_day(params: Mapping[str, Any],
                            section: Section) -> CheckResult:
    result_code = {
        0: "Not Started",
        1: "In Progress",
        2: "Succeeded",
        3: "Succeeded with Errors",
        4: "Failed",
        5: "Aborted",
    }

    status = 0
    problem_list = []
    success_list = []
    date_list = []

    for update in section:
        timestring = update.date.split(' ')[0]
        install_time = datetime.datetime.strptime(timestring, "%m/%d/%Y")
        date_list.append(install_time)
        if int(update.result) in [1, 2]:
            success_list.append(f"{update.date} - {result_code.get(int(update.result))} - {update.name}")
        else:
            problem_list.append(f"{update.date} - {result_code.get(int(update.result))} - {update.name}")

    messagetext = "Last updates installed at " + datetime.datetime.strftime(
        max(date_list), "%d %b %Y") + " - updates shown since " + datetime.datetime.strftime(
        min(date_list), "%d %b %Y")
    messagetext += " - %s updates installed - %s updates with problems" % (
        len(success_list), len(problem_list))
    detailstext = ("Problem updates\n")
    detailstext += ("\n".join(problem_list))
    detailstext += ("\n\nSucceeded updates\n")
    detailstext += ("\n".join(success_list))

    yield Result(state=State(status), summary=messagetext, details=detailstext)


register.check_plugin(
    name="windows_patch_day",
    service_name="Patchday",
    sections=["windows_patch_day"],
    check_default_parameters={},
    discovery_function=discovery_windows_patch_day,
    check_function=check_windows_patch_day,
)

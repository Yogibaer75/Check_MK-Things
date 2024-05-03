#!/usr/bin/env python3
"""Windows last update installed check"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

# Example Output:
# <<<windows_patch_day:sep(124)>>>
# 2024-04 Kumulatives Update für Windows 11 Version 23H2 für x64-basierte Systeme (KB5036980)|04/26/2024 20:07:35|2
# 2024-04 Kumulatives Update für Windows 11 Version 23H2 für x64-basierte Systeme (KB5036980)|04/14/2024 06:40:06|2

import datetime
from typing import List, NamedTuple, Mapping, Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    StringTable,
    check_levels,
)


class WinPatchday(NamedTuple):
    '''one update'''
    name: str
    date: str
    result: str


Section = List[WinPatchday]


def parse_windows_patch_day(string_table: StringTable) -> Section:
    '''parse raw data into list of named tuples'''
    return [
        WinPatchday(name, date, result) for name, date, result in string_table
    ]


agent_section_windows_patch_day = AgentSection(
    name="windows_patch_day",
    parse_function=parse_windows_patch_day,
    parsed_section_name="windows_patch_day",
)


def discovery_windows_patch_day(section: Section) -> DiscoveryResult:
    '''if data is present discover one service'''
    if section:
        yield Service()


def check_windows_patch_day(params: Mapping[str, Any],
                            section: Section) -> CheckResult:
    '''check the status of the last installed updates'''
    if not any(section):
        return None

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
            success_list.append(f"{update.date} - "
                                f"{result_code.get(int(update.result))} - {update.name}")
        else:
            problem_list.append(f"{update.date} - "
                                f"{result_code.get(int(update.result))} - {update.name}")

    messagetext = "Last updates installed at " + datetime.datetime.strftime(
        max(date_list), "%d %b %Y") + " - updates shown since " + datetime.datetime.strftime(
        min(date_list), "%d %b %Y")
    messagetext += (f" - {len(success_list)} updates installed - "
                    f"{len(problem_list)} updates with problems")
    detailstext = "Problem updates\n"
    detailstext += ("\n".join(problem_list))
    detailstext += ("\n\nSucceeded updates\n")
    detailstext += ("\n".join(success_list))

    yield Result(state=State(status), summary=messagetext, details=detailstext)

    newest_update = (datetime.datetime.now() - max(date_list)).days
    if not isinstance(params.get("levels", (30, 90))[0], str):
        levels = ("fixed", params.get("levels", (30, 90)))
    else:
        levels = params.get("levels")

    yield from check_levels(
        value=newest_update,
        levels_upper=levels,
        metric_name="days",
        label="Newest Update",
        render_func=lambda v: f"{v:.1f} d",
    )


check_plugin_windows_patch_day = CheckPlugin(
    name="windows_patch_day",
    service_name="Patchday",
    check_ruleset_name="windows_patch_day",
    sections=["windows_patch_day"],
    check_default_parameters={},
    discovery_function=discovery_windows_patch_day,
    check_function=check_windows_patch_day,
)

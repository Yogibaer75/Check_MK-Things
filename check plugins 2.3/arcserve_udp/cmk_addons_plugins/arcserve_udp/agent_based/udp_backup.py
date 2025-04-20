#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

# Example Output:
# <<<udp_backup:sep(124)>>>
# 1|server1|19.03.2022 18:55:38|2|2|25
# 2|server2||||
#

from typing import Mapping, Any

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


def parse_udp_backup(string_table: StringTable) -> Mapping[str, Mapping[str, Any]]:
    """
    Parse the output of the udp_backup agent plugin.
    The output is a list of lines, each containing the following fields:
    1. Server ID
    2. Server Name
    3. Last Backup Start Time
    4. Last Job Status
    5. RecPoint Status
    6. RecPoint Count
    """
    parsed = {}
    for line in string_table:
        if line[1] != "":
            parsed.setdefault(
                line[1] + "-" + line[0],
                {
                    "lastBackupStartTime": line[2],
                    "lastBackupJobStatus": line[3],
                    "RecPointStatus": line[4],
                    "recPointCount": line[5],
                },
            )
    return parsed


agent_section_udp_backup = AgentSection(
    name="udp_backup",
    parse_function=parse_udp_backup,
)


def discovery_udp_backup(section) -> DiscoveryResult:
    for item, data in section.items():
        if data.get("lastBackupStartTime") == "":
            continue
        yield Service(item=item)


def check_udp_backup(item: str, params: Mapping[str, Any], section) -> CheckResult:
    udp_backup_status = {
        "0": (3, "Unknown"),
        "1": (0, "Finished"),
        "2": (2, "Failed"),
        "3": (0, "Active"),
        "4": (1, "Canceled"),
        "5": (2, "Crashed"),
    }

    udp_recpoint_status = {
        "0": (3, "Unknown", "(!!!)"),
        "1": (0, "OK", ""),
        "2": (1, "Warning", "(!)"),
        "3": (2, "Error", "(!!)"),
    }

    if type(params) is tuple:
        params = {"levels": ("fixed", params)}
    warn_upper, crit_upper = params.get("levels", ("fixed", (None, None)))[1]
    warn_lower, crit_lower = params.get("levels_lower", ("fixed", (None, None)))[1]

    no_backup_state = params.get("no_backup", None)

    if (data:=section.get(item)) is not None:
        print(data)
        status = 0
        msgtext = ""
        last_backup = data.get("lastBackupStartTime")
        last_backup_status = data.get("lastBackupJobStatus")
        rec_status = data.get("RecPointStatus")
        recpoints = data.get("recPointCount")

        if last_backup == "":
            if no_backup_state is not None:
                yield Result(state=State(no_backup_state), summary="No D2D Backup until now")
            else:
                yield Result(state=State.WARN, summary="No D2D Backup until now")
        else:
            msgtext += "Last backup %s," % last_backup
            state, name, state_str = udp_recpoint_status.get(
                rec_status, (3, "Unknown", "(!!!)")
            )
            msgtext += " %s restore points with state %s%s," % (recpoints, name, state_str)
            state, name = udp_backup_status.get(last_backup_status, (3, "unknown"))
            status = max(status, state)
            msgtext += " last backup state %s" % name
            yield Result(state=State(status), summary=msgtext)

            yield from check_levels(
                int(recpoints),
                levels_upper=("fixed", (warn_upper, crit_upper)),
                levels_lower=("fixed", (warn_lower, crit_lower)),
                metric_name="restorepoint",
                notice_only=True,
                label="restore points"
            )


check_plugin_udp_backup = CheckPlugin(
    name="udp_backup",
    service_name="UDP host %s",
    check_ruleset_name="arcserve_udp_backup",
    sections=["udp_backup"],
    check_default_parameters={
        "levels": ("fixed", (36, 72)),
        "levels_lower": ("fixed", (5, 1)),
    },
    discovery_function=discovery_udp_backup,
    check_function=check_udp_backup,
)

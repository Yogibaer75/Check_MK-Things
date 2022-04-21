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
# <<<udp_backup:sep(124)>>>
# 1|server1|19.03.2022 18:55:38|2|2|25
# 2|server2||||
#

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)

from .agent_based_api.v1 import (
    check_levels,
    register,
    Result,
    State,
    Service,
)


def parse_udp_backup(string_table):
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


register.agent_section(
    name="udp_backup",
    parse_function=parse_udp_backup,
)


def discovery_udp_backup(section) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_udp_backup(item: str, params, section) -> CheckResult:
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

    if type(params) == tuple:
        params = {"levels": params}
    warn_upper, crit_upper = params.get("levels")
    warn_lower, crit_lower = params.get("levels_lower")

    no_backup_state = params.get("no_backup", None)

    if section.get(item):
        data = section.get(item)
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
                levels_upper=(warn_upper, crit_upper),
                levels_lower=(warn_lower, crit_lower),
                metric_name="restorepoint",
                notice_only=True,
                label="restore points"
            )


register.check_plugin(
    name="udp_backup",
    service_name="UDP host %s",
    sections=["udp_backup"],
    check_default_parameters={
        "levels": (30, 40),
        "levels_lower": (5, 1),
    },
    discovery_function=discovery_udp_backup,
    check_function=check_udp_backup,
    check_ruleset_name="arcserve_udp_backup",
)

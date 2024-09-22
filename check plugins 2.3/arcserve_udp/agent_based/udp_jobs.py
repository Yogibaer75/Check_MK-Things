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
# <<<udp_jobs:sep(124)>>>
# 1|server1|19.03.2022 17:55:38|3|0|2
# 2|server2||||
#

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)

from .agent_based_api.v1 import (
    check_levels,
    render,
    register,
    Result,
    State,
    Service,
)

import datetime as dt


def parse_udp_jobs(string_table):
    parsed = {}
    for line in string_table:
        if line[1] != "":
            parsed.setdefault(
                line[1] + "-" + line[0],
                {
                    "lastBackupStartTime": line[2],
                    "lastJobStatus": line[3],
                    "jobSize": line[4],
                    "jobMethod": line[5],
                },
            )
    return parsed


register.agent_section(
    name="udp_jobs",
    parse_function=parse_udp_jobs,
)


def _udp_job_age(timedelta):
    return timedelta.days * 24 + int(timedelta.seconds / 3600)


def discovery_udp_jobs(section) -> DiscoveryResult:
    for item in section:
        if section[item].get("lastBackupStartTime") == "":
            continue
        yield Service(item=item)


def check_udp_jobs(item: str, params, section) -> CheckResult:
    udp_job_method = {
        "-1": ("Unknown"),
        "0": ("Full backup job"),
        "1": ("Incremental backup job"),
        "2": ("Verify backup job"),
        "3": ("All"),
        "4": ("File Copy backup job"),
        "5": ("Copy Recovery Point backup job"),
    }

    udp_job_status = {
        "-1": (0, "All"),
        "0": (0, "Active"),
        "1": (0, "Finished"),
        "2": (1, "Canceled"),
        "3": (2, "Failed"),
        "4": (1, "Incomplete"),
        "5": (0, "Idle"),
        "6": (0, "Waiting"),
        "7": (2, "Crash"),
        "9": (1, "License Failed"),
        "10": (2, "Backupjob_PROC_EXIT"),
        "11": (1, "Skipped"),
        "12": (0, "Stop"),
        "10000": (1, "Missed"),
    }

    if type(params) == tuple:
        params = {"levels": params}
    warn, crit = params["levels"]

    no_backup_state = params.get("no_backup", None)

    if section.get(item):
        data = section.get(item)
        msgtext = ""
        last_backup = data.get("lastBackupStartTime")
        job_status = data.get("lastJobStatus")
        size = data.get("jobSize")
        job_method = data.get("jobMethod")

        if last_backup == "":
            if no_backup_state is not None:
                yield Result(state=State(no_backup_state), summary="No UDP job until now")
            else:
                yield Result(state=State.WARN, summary="No UDP job until now")
        else:
            msgtext += "Last job %s," % last_backup
            failed = False
            try:
                last_backup = dt.datetime.strptime(last_backup, "%d.%m.%Y %H:%M:%S")
            except ValueError:
                failed = True
            if failed:
                try:
                    last_backup = dt.datetime.strptime(
                        last_backup, "%m/%d/%Y %I:%M:%S %p"
                    )
                    failed = False
                except ValueError:
                    msgtext += "Last backup time is not in the correct format"
                    failed = True
            if failed:
                backup_age = dt.datetime.now() - dt.datetime.now()
            else:
                backup_age = dt.datetime.now() - last_backup

            backup_age = _udp_job_age(backup_age)
            status, name = udp_job_status.get(job_status, (3, "Unknown"))
            msgtext += " with state %s" % (name)
            method = udp_job_method.get(job_method, "unknown (!!!) id %s" % job_method)
            yield Result(state=State(status), summary=msgtext)

            yield from check_levels(
                int(backup_age * 3600),
                levels_upper=(warn * 3600, crit * 3600),
                render_func=render.timespan,
                notice_only=True,
                metric_name="age",
                label="backup age",
            )

            msgtext = "backup size %s and backup method was %s" % (
                render.bytes(int(size)),
                method,
            )
            yield Result(state=State.OK, summary=msgtext)


register.check_plugin(
    name="udp_jobs",
    service_name="UDP job %s",
    sections=["udp_jobs"],
    check_default_parameters={
        "levels": (36, 72),
    },
    discovery_function=discovery_udp_jobs,
    check_function=check_udp_jobs,
    check_ruleset_name="arcserve_udp_jobs",
)

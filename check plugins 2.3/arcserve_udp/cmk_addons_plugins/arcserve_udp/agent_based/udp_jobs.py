#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

# Example Output:
# <<<udp_jobs:sep(124)>>>
# 1|server1|19.03.2022 17:55:38|3|0|2
# 2|server2||||
#

from typing import Mapping, Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    render,
    Result,
    Service,
    State,
    StringTable,
    check_levels,
)

import datetime as dt


def parse_udp_jobs(string_table: StringTable) -> Mapping[str, Mapping[str, Any]]:
    """
    Parse the output of the udp_jobs agent plugin.
    The output is a list of lines, each containing the following fields:
    1. Server ID
    2. Server Name
    3. Last Backup Start Time
    4. Last Job Status
    5. Job Size
    6. Job Method
    """
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


agent_section_udp_jobs = AgentSection(
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


def check_udp_jobs(item: str, params: Mapping[str, Any], section) -> CheckResult:
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

    if type(params) is tuple:
        params = {"levels": ("fixed",params)}
    warn, crit = params["levels"][1]

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
                levels_upper=("fixed", (warn * 3600, crit * 3600)),
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


check_plugin_udp_jobs = CheckPlugin(
    name="udp_jobs",
    service_name="UDP job %s",
    check_ruleset_name="arcserve_udp_jobs",
    sections=["udp_jobs"],
    check_default_parameters={
        "levels": ("fixed", (36, 72)),
    },
    discovery_function=discovery_udp_jobs,
    check_function=check_udp_jobs,
)
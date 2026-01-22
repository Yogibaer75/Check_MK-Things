#!/usr/bin/env python3
"""Windows Netback Job status check"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

# Example Output:
# <<<netbackup_jobs>>>
# STATUS CLIENT        POLICY           SCHED      SERVER      TIME COMPLETED
#  0    srv-bk23      NB_CAT_HOT       Full_Day_B srv-bk23    09/23/2025 16:00:27
#  0    srv-bk23      NB_CAT_HOT       Full_Day_B srv-bk23    09/23/2025 16:00:28

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
)


class NetbackupJob(NamedTuple):
    """one update"""

    state: int
    client: str
    policy: str
    sched: str
    server: str
    date: str


Section = List[NetbackupJob]


def parse_netbackup_jobs(string_table: StringTable) -> Section:
    """parse raw data into list of named tuples"""
    updates: Section = []
    for line in string_table:
        if line[0] == "STATUS":
            continue
        if len(line) < 7 or len(line) > 7:
            continue
        state, client, policy, sched, server, date, time = line
        updates.append(NetbackupJob(state, client, policy, sched, server, f"{date} {time}"))
    return updates


agent_section_netbackup_jobs = AgentSection(
    name="netbackup_jobs",
    parse_function=parse_netbackup_jobs,
    parsed_section_name="netbackup_jobs",
)


def discovery_netbackup_jobs(section: Section) -> DiscoveryResult:
    """if data is present discover one service"""
    if section:
        yield Service()


def check_netbackup_jobs(params: Mapping[str, Any], section: Section) -> CheckResult:
    """check the status of the last installed updates"""
    if not any(section):
        yield Result(
            state=State(0),
            summary=("No information found for backup"),
        )
        return

    result_code = {
        0: ("Successful", 0),
        1: ("partially Successful", 1),
        2: ("non of the files were backed up", 1),
        3: ("valid image archive created, but no files deleted", 1),
        4: ("archive file removal failed", 2),
        5: ("the restore failed to recover the file(s)", 2),
    }

    status = 0
    problem_list = []
    success_list = []
    date_list = []

    for job in section:
        timestring = job.date.split(" ")[0]
        date_list.append(datetime.datetime.strptime(timestring, "%m/%d/%Y"))
        if int(job.state) in [0]:
            success_list.append(
                f"{job.date} - "
                f"{result_code.get(int(job.state))} - {job.client} - {job.policy}"
            )
        else:
            problem_list.append(
                f"{job.date} - "
                f"{result_code.get(int(job.state), (f"Unknown State ({job.state})", 3))[0]} - "
                f"{job.client} - {job.policy}"
            )

    messagetext = (
        "Last backup "
        f"{datetime.datetime.strftime(max(date_list), "%d %b %Y")}"
        f" - {len(success_list)} backups successful - "
        f"{len(problem_list)} backups with problems"
    )
    detailstext = (
        f"Problem backups\n{'\n'.join(problem_list)}"
    )
    if len(problem_list) > 0:
        status = 1

    yield Result(state=State(status), summary=messagetext, details=detailstext)


check_plugin_netbackup_jobs = CheckPlugin(
    name="netbackup_jobs",
    service_name="Netbackup Job Status",
    check_ruleset_name="netbackup_jobs",
    sections=["netbackup_jobs"],
    check_default_parameters={},
    discovery_function=discovery_netbackup_jobs,
    check_function=check_netbackup_jobs,
)

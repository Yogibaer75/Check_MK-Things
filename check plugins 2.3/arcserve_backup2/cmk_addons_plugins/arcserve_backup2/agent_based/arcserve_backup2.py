#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

# Example Output:
#<<<arcserver_backup2:sep(124)>>>
#jobid|logtime|serverhost|agenthost|msgtextid|msgtext
#9034|02.01.2024 12:03:43|BACK02||4354|Vorgang Datenbank bereinigen erfolgreich
#9034|02.01.2024 12:00:01|BACK02||7936|Ausführung von Job Datenbank bereinigen geplant für 02.01.24 um 12:00.
#

from typing import Any, Mapping

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

Section = Mapping[str, Any]


def parse_arcserve_backup2(string_table: StringTable) -> Section:
    parsed = {}
    headers = string_table[0]
    for line in string_table[1:]:
        data_dict = dict(zip(headers,line))
        jobid = data_dict.get('jobid')
        if not jobid:
            continue
        if jobid not in parsed.keys():
            parsed.setdefault(int(jobid), {}),
        if data_dict.get('agenthost'):
            client = data_dict.get('agenthost')
        else:
            client = "---"
        if not parsed[int(jobid)].get(data_dict['msgtextid']):
            parsed[int(jobid)].setdefault(data_dict['msgtextid'], [f"{client} - {data_dict.get('msgtext')}"])
        else:
            parsed[int(jobid)][data_dict['msgtextid']].append(f"{client} - {data_dict.get('msgtext')}")

    return parsed


agent_section_arcserve_backup2 = AgentSection(
    name="arcserve_backup2",
    parse_function=parse_arcserve_backup2,
)


def discovery_arcserve_backup2(section: Section) -> DiscoveryResult:
    if section:
        yield Service()


def check_arcserve_backup2(section: Section) -> CheckResult:
    worst = 0
    failed_ids = []
    database_cleanup_found = False
    for job, data in section.items():
        status = 0
        if "4354" in data.keys() and "7936" in data.keys():
            if [i for i in data.get('4354', '') if "Datenbank bereinigen" in i] and database_cleanup_found:
                continue
            message = f"ID {job} - {data.get('7936',[''])[0].replace('--- - ','')} - {data.get('4354','')[0].replace('--- - ','')}"
            if not [i for i in data.get('4354', '') if "erfolgreich" in i]:
                status = 1
                failed_ids.append(job)
            if [i for i in data.get('4354', '') if "Datenbank bereinigen" in i]:
                database_cleanup_found = True
        elif "4354" in data.keys() and "4498" in data.keys():
            message = f"ID {job} - {data.get('4498',[''])[0].replace('--- - ','')} - {data.get('4354','')[0].replace('--- - ','')}"
            if not [i for i in data.get('4354', '') if "erfolgreich" in i]:
                status = 1
                failed_ids.append("%s" % job)
        elif "4354" in data.keys():
            continue
        else:
            message = f"ID {job} - {data.get('4498',[''])[0].replace('--- - ','')} started but not finished until now"
        worst = max(status, worst)
        yield Result(state=State(status), notice=message)
    if failed_ids:
        summary_msg = f"Jobs {','.join(failed_ids)} with problems"
    else:
        summary_msg = "All Jobs without problems"

    yield Result(state=State(worst), summary=summary_msg)


check_plugin_arcserve_backup2 = CheckPlugin(
    name="arcserve_backup2",
    service_name="Arcserve Backup Status",
    sections=["arcserve_backup2"],
    discovery_function=discovery_arcserve_backup2,
    check_function=check_arcserve_backup2,
)

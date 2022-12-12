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
import ast
import time
from typing import Any, Dict, Mapping

from .agent_based_api.v1 import register, render, Result, Service, State, Metric
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, StringTable
from cmk.base.check_api import get_filesize_human_readable, get_bytes_human_readable
Section = Dict[str, Mapping[str, Any]]


def parse_prism_protection_domains(string_table: StringTable) -> Section:
    parsed: Section = {}
    data = ast.literal_eval(string_table[0][0])
    for element in data.get("entities"):
        parsed.setdefault(element.get("name", "unknown"), element)
    return parsed


register.agent_section(
    name="prism_protection_domains",
    parse_function=parse_prism_protection_domains,
)


def discovery_prism_protection_domains(section: Section) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_prism_protection_domains(
    item: str, 
    params: Mapping[str, Any], 
    section: Section) -> CheckResult:

    data = section.get(item)
#    if not data:
#        return

    mtr = data.get("metro_avail", None)

    if mtr is not None:
        type = "Metro Availability"
        summary=(f"Type: {type}, "
            f"Role: {mtr['role']}, "
            f"Container: {mtr['container']}, "
            f"RemoteSite: {mtr['remote_site_names']}, ")

        if mtr.get("status") == "Enabled":

            summary += "Status: Enabled and in Sync"
            state = State.OK
        elif mtr.get("status") == "Synchronizing":
            summary += f"Status: {mtr['status']} and in Sync"
            state = State.WARN
        else:
            summary += f"Status: {mtr['status']} and in Sync"
            state=State.CRIT

        yield Result(state=state, summary=summary)


    elif mtr is None:
        type = "Async DR"
        mtr_role = remote_mtr = container_mtr = status_mtr = "N/A"  
        date = data.get("next_snapshot_time_usecs", "N/A")
        if date is None:
            date = "N/A"
        else:
            date = time.strftime('%a %d-%m-%Y %H:%M:%S', time.localtime(float(date)))

        remote = data.get("remote_site_names")
        if len(remote) == 0:
            remote = "N/A"

        exclusivesnapshot = float(data["usage_stats"].get("dr.exclusive_snapshot_usage_bytes"))
        yield Metric("pd_exclusivesnapshot", 
            exclusivesnapshot)
        yield Metric("pd_bandwidthtx",
            float(data["stats"].get("replication_received_bandwidth_kBps")))
        yield Metric("pd_bandwidthrx",
            float(data["stats"].get("replication_transmitted_bandwidth_kBps")))
            

        summary = (f"Type: {type}, "
            f"Exclusive Snapshot Usage: {get_bytes_human_readable(exclusivesnapshot)}, "
            f"Next Snapshot scheduled at: {date}, "
            f"Total entities: {len(data['vms'])}, "
            f"Remote Site: {remote}")


        yield Result(state=State.OK, summary=summary)


register.check_plugin(
    name="prism_protection_domains",
    service_name="NTNX Data Protection %s",
    sections=["prism_protection_domains"],
    check_default_parameters={},
    discovery_function=discovery_prism_protection_domains,
    check_function=check_prism_protection_domains,
    check_ruleset_name="prism_protection_domains",
)

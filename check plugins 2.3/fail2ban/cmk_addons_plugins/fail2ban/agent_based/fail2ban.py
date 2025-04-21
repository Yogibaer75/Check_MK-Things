#!/usr/bin/env python3

# (c) Jens Kühnel <fail2ban-checkmk@jens.kuehnel.org> 2021
# migrated to CMK 2.3 Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
#
# Information about fail2ban check_mk module see:
# https://github.com/JensKuehnel/fail2ban-check-mk
#
# License: GNU General Public License v2

# Example for output from agent
# ---------------------------------------------------------
# <<<fail2ban>>>
# Detected jails: 	postfix-sasl  sshd
# Status for the jail: postfix-sasl
# |- Filter
# |  |- Currently failed:	7
# |  |- Total failed:	1839
# |  `- Journal matches:	_SYSTEMD_UNIT=postfix.service
# `- Actions
#    |- Currently banned:	1
#    |- Total banned:	76
#    `- Banned IP list:	212.70.149.71
# Status for the jail: sshd
# |- Filter
# |  |- Currently failed:	6
# |  |- Total failed:	1066
# |  `- Journal matches:	_SYSTEMD_UNIT=sshd.service + _COMM=sshd
# `- Actions
#    |- Currently banned:	5
#    |- Total banned:	50
#    `- Banned IP list:	112.122.54.162 144.135.85.184 103.200.21.89 1.14.61.204

from typing import Mapping, Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    Metric,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    StringTable,
    check_levels,
)
from more_itertools import first


def parse_fail2ban(string_table: StringTable) -> Mapping[str, Any]:
    """
    Parse the output of the fail2ban agent section.
    """
    # The first line is the header
    # The rest is the data
    # We need to split the lines into sections
    # Each section starts with "Status for the jail: "
    firstline = first(string_table)
    if firstline[:2] != ["Detected", "jails:"]:
        # If the first line is not "Detected jails: ", raise an error
        raise ValueError("Invalid fail2ban output: missing header")
    jails = firstline[2:]
    sections = {}
    for line in string_table[1:]:
        # If the line starts with "Status for the jail: ", start a new section
        if line[:4] == ["Status", "for", "the", "jail:"]:
            jail = line[4]
            if jail not in jails:
                # If the jail is not in the list of jails, raise an error
                print(f"Invalid fail2ban output: unknown jail {jail}")
            if jail not in sections:
                sections[jail] = {}
        elif (line[:4]) == [
            "|",
            "|-",
            "Currently",
            "failed:",
        ]:
            # If the line starts with "| | - Currently failed: ", add it to the current section
            if jail is None:
                continue
            sections[jail]["currentfailed"] = int(line[4])
        elif (line[:4]) == [
            "|",
            "|-",
            "Total",
            "failed:",
        ]:
            if jail is None:
                continue
            sections[jail]["totalfailed"] = int(line[4])
        elif (line[:3]) == [
            "|-",
            "Currently",
            "banned:",
        ]:
            if jail is None:
                continue
            sections[jail]["currentbanned"] = int(line[3])
        elif (line[:3]) == [
            "|-",
            "Total",
            "banned:",
        ]:
            if jail is None:
                continue
            sections[jail]["totalbanned"] = int(line[3])
        continue
    return sections


agent_section_fail2ban = AgentSection(
    name="fail2ban",
    parse_function=parse_fail2ban,
)


def discovery_fail2ban(section) -> DiscoveryResult:
    """
    Discover the fail2ban jails.
    """
    for jail in section:
        yield Service(item=jail)


def check_fail2ban(item, params, section) -> CheckResult:
    data = section.get(item)
    if data is None:
        # If the jail is not in the list of jails, return
        return

    yield Result(state=State.OK, summary=f"{item} active")

    yield from check_levels(
        value=int(data["currentfailed"]),
        levels_upper=params["failed"],
        metric_name="current_failed",
        label="Current Failed",
        render_func=lambda x: f"{x} failed",
    )

    yield from check_levels(
        value=int(data["currentbanned"]),
        levels_upper=params["banned"],
        metric_name="current_banned",
        label="Current Banned",
        render_func=lambda x: f"{x} banned",
    )

    yield Metric(name="total_failed", value=int(data["totalfailed"]))
    yield Metric(name="total_banned", value=int(data["totalbanned"]))


check_plugin_fail2ban = CheckPlugin(
    name="fail2ban",
    service_name="Jail %s",
    discovery_function=discovery_fail2ban,
    check_function=check_fail2ban,
    check_default_parameters={
        "banned": ("fixed", (10, 20)),
        "failed": ("fixed", (30, 40)),
    },
    check_ruleset_name="fail2ban",
)

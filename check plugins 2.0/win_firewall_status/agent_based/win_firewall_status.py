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

# <<<win_firewall_status:sep(124)>>>
# Profile|Enabled|Inbound|Outbound
# Domain|True|Block|Allow
# Private|True|Block|Allow
# Public|True|Block|Allow

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)

from .agent_based_api.v1 import (
    register,
    Result,
    State,
    Service,
)


def parse_win_firewall_status(string_table):
    key = "Profile"
    parsed = {}
    for i in string_table[1:]:
        element = dict(zip(string_table[0], i))
        parsed[element[key]] = element

    return parsed


register.agent_section(
    name="win_firewall_status",
    parse_function=parse_win_firewall_status,
)


def discovery_win_firewall_status(section) -> DiscoveryResult:
    yield Service(item="Status")


def check_win_firewall_status(item, params, section) -> CheckResult:

    for item in section:
        for element in params.get("profiles"):
            if item == element[0]:
                _profile, status, inbound, outbound = element
        data = section[item]
        state = 0
        status_active = data.get("Enabled")
        inbound_active = data.get("Inbound")
        outbound_active = data.get("Outbound")

        if status != status_active:
            state = max(state, 1)
            yield Result(
                state=State.WARN,
                summary=
                "Profile %s operational state is not as expected %s vs. %s" %
                (item, status, status_active))

        if inbound != inbound_active:
            state = max(state, 1)
            yield Result(
                state=State.WARN,
                summary="Profile %s Inbound state is not as expected %s vs. %s"
                % (item, inbound, inbound_active))

        if outbound != outbound_active:
            state = max(state, 1)
            yield Result(
                state=State.WARN,
                summary="Profile %s Outbound state is not as expected %s vs. %s"
                % (item, outbound, outbound_active))

        if state == 0:
            yield Result(state=State.OK,
                         summary="Profile %s as expected" % item)


register.check_plugin(
    name="win_firewall_status",
    service_name="Windows Firewall %s",
    sections=["win_firewall_status"],
    discovery_function=discovery_win_firewall_status,
    check_function=check_win_firewall_status,
    check_default_parameters={
        'profiles': [('Domain', 'True', 'Block', 'Allow'),
                     ('Privat', 'True', 'Block', 'Allow'),
                     ('Public', 'True', 'Block', 'Allow')]
    },
    check_ruleset_name="win_firewall_status",
)

#!/usr/bin/env python3
"""Windows Firewall status check"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

# Example Output:

# <<<win_firewall_status:sep(124)>>>
# Profile|Enabled|Inbound|Outbound
# Domain|True|Block|Allow
# Private|True|Block|Allow
# Public|True|Block|Allow

from typing import Any, Dict, Tuple
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
    StringTable,
)

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
    Result,
    State,
    Service,
)

Section = Dict[str, Any]


def parse_win_firewall_status(string_table: StringTable) -> Section:
    """parse raw data into dictionary"""
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


def discovery_win_firewall_status(section: Section) -> DiscoveryResult:
    """if data is present discover service"""
    if section:
        yield Service()


def _get_params(params: Dict[str, Any], profile) -> Tuple:
    for element in params.get("profiles", []):
        if not element:
            continue
        if element[0] == profile:
            return element
    return (None, None, None, None)


def check_win_firewall_status(params: Dict[str, Any], section: Section) -> CheckResult:
    """check the firewall state compared to params"""
    for key, data in section.items():
        _profile, status, inbound, outbound = _get_params(params, key)
        state = 0
        status_active = data.get("Enabled")
        inbound_active = data.get("Inbound")
        outbound_active = data.get("Outbound")

        if status != status_active:
            state = max(state, 1)
            yield Result(
                state=State.WARN,
                summary=(f"Profile {key} operational state is not "
                         f"as expected {status} vs. {status_active}"),
            )

        if inbound != inbound_active:
            state = max(state, 1)
            yield Result(
                state=State.WARN,
                summary=(f"Profile {key} Inbound state is not as "
                         f"expected {inbound} vs. {inbound_active}"),
            )

        if outbound != outbound_active:
            state = max(state, 1)
            yield Result(
                state=State.WARN,
                summary=(f"Profile {key} Outbound state is not as "
                         f"expected {outbound} vs. {outbound_active}"),
            )

        if state == 0:
            yield Result(state=State.OK, summary=f"Profile {key} as expected")


register.check_plugin(
    name="win_firewall_status",
    service_name="Windows Firewall Status",
    sections=["win_firewall_status"],
    discovery_function=discovery_win_firewall_status,
    check_function=check_win_firewall_status,
    check_default_parameters={
        "profiles": [
            ("Domain", "True", "Block", "Allow"),
            ("Private", "True", "Block", "Allow"),
            ("Public", "True", "Block", "Allow"),
        ]
    },
    check_ruleset_name="win_firewall_status",
)

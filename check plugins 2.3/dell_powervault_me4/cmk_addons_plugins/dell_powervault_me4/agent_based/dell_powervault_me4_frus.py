#!/usr/bin/env python3
"""Dell ME4 FRUs check"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2


from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)
from cmk_addons.plugins.dell_powervault_me4.lib import parse_dell_powervault_me4

agent_section_dell_powervault_me4_frus = AgentSection(
    name="dell_powervault_me4_frus",
    parse_function=parse_dell_powervault_me4,
)


def discovery_dell_powervault_me4_frus(section) -> DiscoveryResult:
    """one service is discovered for every FRU"""
    for item in section:
        yield Service(item=item)


def check_dell_powervault_me4_frus(item: str, params, section) -> CheckResult:
    """check the state of the FRU"""
    data = section.get(item, {})
    if not data:
        return
    fru_states = {
        0: ("OK", 0),
        1: ("Degraded", 1),
        2: ("Fault", 2),
        3: ("Unknown", 3),
    }

    state_text, status_num = fru_states.get(
        data.get("fru-status-numeric", 5), ("N/A", 0)
    )
    message = f"{data.get('description', 'Unknown')} state is {state_text}"

    yield Result(state=State(status_num), summary=message)


check_plugin_dell_powervault_me4_frus = CheckPlugin(
    name="dell_powervault_me4_frus",
    service_name="Fru %s",
    sections=["dell_powervault_me4_frus"],
    check_default_parameters={
        "fru_state": 0,
    },
    discovery_function=discovery_dell_powervault_me4_frus,
    check_function=check_dell_powervault_me4_frus,
    check_ruleset_name="dell_powervault_me4_frus",
)

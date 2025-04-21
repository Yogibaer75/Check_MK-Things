#!/usr/bin/env python3
"""Dell ME4 system check"""

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

agent_section_dell_powervault_me4_system = AgentSection(
    name="dell_powervault_me4_system",
    parse_function=parse_dell_powervault_me4,
)


def discovery_dell_powervault_me4_system(section) -> DiscoveryResult:
    """for every system a service is discovered"""
    for item in section:
        yield Service(item=item)


def check_dell_powervault_me4_system(item: str, params, section) -> CheckResult:
    """check the state of the system"""
    data = section.get(item, {})
    if not data:
        return
    system_states = {
        0: ("OK", 0),
        1: ("Degraded", 1),
        2: ("Fault", 2),
        3: ("Unknown", 3),
    }

    state_text, status_num = system_states.get(
        data.get("health-numeric", 3), ("Unknown", 3)
    )
    message = f"with serial {data.get('midplane-serial-number')} is {state_text}"

    yield Result(state=State(status_num), summary=message)


check_plugin_dell_powervault_me4_system = CheckPlugin(
    name="dell_powervault_me4_system",
    service_name="System %s",
    sections=["dell_powervault_me4_system"],
    check_default_parameters={
        "system_state": 0,
    },
    discovery_function=discovery_dell_powervault_me4_system,
    check_function=check_dell_powervault_me4_system,
    check_ruleset_name="dell_powervault_me4_system",
)

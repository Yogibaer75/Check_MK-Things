#!/usr/bin/env python3
"""Dell ME4 controllers check"""

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

agent_section_dell_powervault_me4_controllers = AgentSection(
    name="dell_powervault_me4_controllers",
    parse_function=parse_dell_powervault_me4,
)


def discovery_dell_powervault_me4_controllers(section) -> DiscoveryResult:
    """for every controller one service is dicovered"""
    for item in section:
        yield Service(item=item)


def check_dell_powervault_me4_controllers(item: str, params, section) -> CheckResult:
    """check the state of the controller"""
    data = section.get(item, {})
    if not data:
        return
    ctrl_states = {
        0: ("OK", 0),
        1: ("Degraded", 1),
        2: ("Fault", 2),
        3: ("Unknown", 3),
    }

    state_text, status_num = ctrl_states.get(
        data.get("health-numeric", 3), ("Unknown", 3)
    )
    message = f"{data.get('description')} is {state_text}"
    yield Result(state=State(status_num), summary=message)


check_plugin_dell_powervault_me4_controllers = CheckPlugin(
    name="dell_powervault_me4_controllers",
    service_name="Controller %s",
    sections=["dell_powervault_me4_controllers"],
    check_default_parameters={
        "ctrl_state": 0,
    },
    discovery_function=discovery_dell_powervault_me4_controllers,
    check_function=check_dell_powervault_me4_controllers,
    check_ruleset_name="dell_powervault_me4_controllers",
)

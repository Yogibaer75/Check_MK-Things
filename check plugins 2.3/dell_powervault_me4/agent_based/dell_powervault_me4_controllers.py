#!/usr/bin/env python3
"""Dell ME4 controllers check"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2


from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
    Result,
    State,
    Service,
)

from .utils.dell_powervault_me4 import parse_dell_powervault_me4

register.agent_section(
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


register.check_plugin(
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

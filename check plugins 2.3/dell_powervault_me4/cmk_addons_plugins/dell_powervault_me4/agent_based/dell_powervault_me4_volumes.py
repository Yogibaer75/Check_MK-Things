#!/usr/bin/env python3
"""Dell ME4 volumes check"""

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

agent_section_dell_powervault_me4_volumes = AgentSection(
    name="dell_powervault_me4_volumes",
    parse_function=parse_dell_powervault_me4,
)


def discovery_dell_powervault_me4_volumes(section) -> DiscoveryResult:
    """for every volume a service is discovered"""
    for item in section:
        yield Service(item=item)


def check_dell_powervault_me4_volumes(item: str, params, section) -> CheckResult:
    """check the state of the volume"""
    data = section.get(item, {})
    if not data:
        return
    vol_states = {
        0: ("OK", 0),
        1: ("Degraded", 1),
        2: ("Fault", 2),
        3: ("Unknown", 3),
    }

    state_text, status_num = vol_states.get(
        data.get("health-numeric", 3), ("Unknown", 3)
    )
    message = f"{data.get('volume-name')} with {data.get('total-size')} total size is {state_text}"
    yield Result(state=State(status_num), summary=message)


check_plugin_dell_powervault_me4_volumes = CheckPlugin(
    name="dell_powervault_me4_volumes",
    service_name="Volume %s",
    sections=["dell_powervault_me4_volumes"],
    check_default_parameters={
        "vol_state": 0,
    },
    discovery_function=discovery_dell_powervault_me4_volumes,
    check_function=check_dell_powervault_me4_volumes,
    check_ruleset_name="dell_powervault_me4_volumes",
)

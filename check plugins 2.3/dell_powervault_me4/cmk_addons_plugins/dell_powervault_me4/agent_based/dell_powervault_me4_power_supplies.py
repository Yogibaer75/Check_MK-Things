#!/usr/bin/env python3
"""Dell ME4 PSU check"""

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

agent_section_dell_powervault_me4_power_supplies = AgentSection(
    name="dell_powervault_me4_power_supplies",
    parse_function=parse_dell_powervault_me4,
)


def discovery_dell_powervault_me4_power_supplies(section) -> DiscoveryResult:
    """for every PSU a service is discovered"""
    for item in section:
        yield Service(item=item)


def check_dell_powervault_me4_power_supplies(
    item: str, params, section
) -> CheckResult:
    """check the state of the PSU"""
    data = section.get(item, {})
    if not data:
        return
    psu_states = {
        0: ("OK", 0),
        1: ("Degraded", 1),
        2: ("Fault", 2),
        3: ("Unknown", 3),
    }

    state_text, status_num = psu_states.get(
        data.get("health-numeric", 3), ("Unknown", 3)
    )
    message = f"{data.get('description', 'Unknown')} state is {state_text}"

    yield Result(state=State(status_num), summary=message)


check_plugin_dell_powervault_me4_power_supplies = CheckPlugin(
    name="dell_powervault_me4_power_supplies",
    service_name="PSU %s",
    sections=["dell_powervault_me4_power_supplies"],
    check_default_parameters={
        "psu_state": 0,
    },
    discovery_function=discovery_dell_powervault_me4_power_supplies,
    check_function=check_dell_powervault_me4_power_supplies,
    check_ruleset_name="dell_powervault_me4_power_supplies",
)

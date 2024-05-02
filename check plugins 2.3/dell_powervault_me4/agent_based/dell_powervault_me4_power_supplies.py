#!/usr/bin/env python3
"""Dell ME4 PSU check"""

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


register.check_plugin(
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

#!/usr/bin/env python3
"""Dell ME4 pools check"""

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

agent_section_dell_powervault_me4_pools = AgentSection(
    name="dell_powervault_me4_pools",
    parse_function=parse_dell_powervault_me4,
)


def discovery_dell_powervault_me4_pools(section) -> DiscoveryResult:
    """for every pool a service is discovered"""
    for item in section:
        yield Service(item=item)


def check_dell_powervault_me4_pools(item: str, params, section) -> CheckResult:
    """check the state of the pool"""
    data = section.get(item, {})
    if not data:
        return
    pool_states = {
        0: ("OK", 0),
        1: ("Degraded", 1),
        2: ("Fault", 2),
        3: ("Unknown", 3),
    }

    state_text, status_num = pool_states.get(
        data.get("health-numeric", 3), ("Unknown", 3)
    )
    message = f"Pool {data.get('name')} with {data.get('total-size')} \
                total size is {state_text}, available capacity {data.get('total-avail')}"

    yield Result(state=State(status_num), summary=message)


check_plugin_dell_powervault_me4_pools = CheckPlugin(
    name="dell_powervault_me4_pools",
    service_name="Pool %s",
    sections=["dell_powervault_me4_pools"],
    check_default_parameters={
        "pool_state": 0,
    },
    discovery_function=discovery_dell_powervault_me4_pools,
    check_function=check_dell_powervault_me4_pools,
    check_ruleset_name="dell_powervault_me4_pools",
)

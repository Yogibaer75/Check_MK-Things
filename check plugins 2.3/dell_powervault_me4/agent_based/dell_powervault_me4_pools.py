#!/usr/bin/env python3
"""Dell ME4 pools check"""

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


register.check_plugin(
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

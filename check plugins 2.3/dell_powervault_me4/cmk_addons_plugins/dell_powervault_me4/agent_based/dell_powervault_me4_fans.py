#!/usr/bin/env python3
"""Dell ME4 fans check"""

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
    check_levels,
)
from cmk_addons.plugins.dell_powervault_me4.lib import parse_dell_powervault_me4

agent_section_dell_powervault_me4_fans = AgentSection(
    name="dell_powervault_me4_fans",
    parse_function=parse_dell_powervault_me4,
)


def discovery_dell_powervault_me4_fans(section) -> DiscoveryResult:
    """for every fan one service is discovered"""
    for item in section:
        yield Service(item=item)


def check_dell_powervault_me4_fans(item: str, params, section) -> CheckResult:
    """check the state of the fan"""
    data = section.get(item, {})
    if not data:
        return
    disk_states = {
        0: ("OK", 0),
        1: ("Degraded", 1),
        2: ("Fault", 2),
        3: ("Unknown", 3),
    }

    state_text, status_num = disk_states.get(
        data.get("health-numeric", 3), ("Unknown", 3)
    )
    message = f"{data.get('name')} {data.get('location', 'Unknown')} is {state_text}"

    yield Result(state=State(status_num), summary=message)

    value = int(data.get("speed"))

    yield from check_levels(
        value=value,
        metric_name="fan",
        levels_upper=params["levels"],
        levels_lower=params["levels_lower"],
        render_func=lambda retval: f"{retval}:.2f rpm",
        boundaries=(0, None),
    )


check_plugin_dell_powervault_me4_fans = CheckPlugin(
    name="dell_powervault_me4_fans",
    service_name="Fan %s",
    sections=["dell_powervault_me4_fans"],
    check_default_parameters={
        "fan_state": 0,
        "levels": ("fixed", (8000, 9000)),
        "levels_lower": ("fixed", (1500, 1000)),
    },
    discovery_function=discovery_dell_powervault_me4_fans,
    check_function=check_dell_powervault_me4_fans,
    check_ruleset_name="dell_powervault_me4_fans",
)

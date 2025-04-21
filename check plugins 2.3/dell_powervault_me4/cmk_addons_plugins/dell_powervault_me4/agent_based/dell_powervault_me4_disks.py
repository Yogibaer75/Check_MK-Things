#!/usr/bin/env python3
"""Dell ME4 disks check"""

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
    get_value_store,
)
from cmk.plugins.lib.temperature import TempParamDict, check_temperature
from cmk_addons.plugins.dell_powervault_me4.lib import parse_dell_powervault_me4

agent_section_dell_powervault_me4_disks = AgentSection(
    name="dell_powervault_me4_disks",
    parse_function=parse_dell_powervault_me4,
)


def discovery_dell_powervault_me4_disks(section) -> DiscoveryResult:
    """for every disk a service is discovered"""
    for item in section:
        yield Service(item=item)


def check_dell_powervault_me4_disks(
    item: str, params: TempParamDict, section
) -> CheckResult:
    """check the state of the disk"""
    data = section.get(item, {})
    if not data:
        return
    disk_states = {
        0: ("OK", 0),
        1: ("Degraded", 1),
        2: ("Fault", 2),
        3: ("Unknown", 3),
    }

    usage_numeric = {
        0: "AVAIL",
        3: "GLOBAL SP",
        5: "LEFTOVR",
        7: "FAILED",
        8: "UNUSABLE",
        9: "VIRTUAL POOL",
    }

    state_text, status_num = disk_states.get(
        data.get("health-numeric", 3), ("Unknown", 3)
    )
    message = f"{data.get('description', 'Unknown')} disk with \
                size {data.get('size')} is {state_text}"
    if status_num == 3 and data.get("usage-numeric") == 3:
        state_text, status_num = ("Global SP", 0)

    disk_usage = usage_numeric.get(data.get("usage-numeric"))
    message += f", disk usage is {disk_usage}"

    yield Result(state=State(status_num), summary=message)

    value = data.get("temperature")
    value_number = "".join(c for c in value if (c.isdigit() or c == "."))

    yield from check_temperature(
        float(value_number),
        params,
        unique_name=f"m4.disk.temp.{item}",
        value_store=get_value_store(),
    )


check_plugin_dell_powervault_me4_disks = CheckPlugin(
    name="dell_powervault_me4_disks",
    service_name="Disk %s",
    sections=["dell_powervault_me4_disks"],
    check_default_parameters={},
    discovery_function=discovery_dell_powervault_me4_disks,
    check_function=check_dell_powervault_me4_disks,
    check_ruleset_name="temperature",
)

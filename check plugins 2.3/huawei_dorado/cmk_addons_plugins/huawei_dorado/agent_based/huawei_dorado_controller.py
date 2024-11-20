#!/usr/bin/env python3
'''Controller check'''
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    Result,
    State,
)
from cmk_addons.plugins.huawei_dorado.lib import (
    HuaweiAPIData,
    parse_huawei_dorado,
    discover_huawei_dorado_items,
    check_huawei_health,
)

agent_section_huawei_dorado_controller = AgentSection(
    name="huawei_dorado_controller",
    parse_function=parse_huawei_dorado,
    parsed_section_name="huawei_dorado_controller",
)


def check_huawei_dorado_controller(item: str, section: HuaweiAPIData) -> CheckResult:
    '''check state of the controller'''
    data = section.get(item)
    if not data:
        return

    state = check_huawei_health(data)
    for key, health in state.items():
        yield Result(state=State(health[1]), summary=f"{key}: {health[0]}")

    msg = f"Location: {data.get('LOCATION')}\n"
    yield Result(state=State(0), notice="empty", details=msg)


check_plugin_huawei_dorado_controller = CheckPlugin(
    name="huawei_dorado_controller",
    service_name="Controller %s",
    sections=["huawei_dorado_controller"],
    discovery_function=discover_huawei_dorado_items,
    check_function=check_huawei_dorado_controller,
)

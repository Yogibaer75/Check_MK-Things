#!/usr/bin/env python3
'''Disk check'''
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    Result,
    State,
    get_value_store,
)
from cmk.plugins.lib.temperature import TempParamDict, check_temperature
from cmk_addons.plugins.huawei_dorado.lib import (
    HuaweiAPIData,
    parse_huawei_dorado,
    discover_huawei_dorado_items,
    check_huawei_health,
)

agent_section_huawei_dorado_disk = AgentSection(
    name="huawei_dorado_disk",
    parse_function=parse_huawei_dorado,
    parsed_section_name="huawei_dorado_disk",
)


def check_huawei_dorado_disk(
    item: str, params: TempParamDict, section: HuaweiAPIData
) -> CheckResult:
    """check disk state"""
    data = section.get(item)
    if not data:
        return

    yield from check_temperature(
        int(data.get("TEMPERATURE", 0)),
        params,
        unique_name=f"huawei.temp.{data.get('ID')}",
        value_store=get_value_store(),
    )

    state = check_huawei_health(data)
    for key, health in state.items():
        yield Result(state=State(health[1]), summary=f"{key}: {health[0]}")

    msg = (
        f"Model: {data.get('MODEL')}\n"
        f"Runtime: {data.get('RUNTIME')} days\n"
        f"Location: {data.get('LOCATION')}\n"
    )
    yield Result(state=State(0), notice="empty", details=msg)


check_plugin_huawei_dorado_disk = CheckPlugin(
    name="huawei_dorado_disk",
    service_name="Disk %s",
    sections=["huawei_dorado_disk"],
    discovery_function=discover_huawei_dorado_items,
    check_function=check_huawei_dorado_disk,
    check_default_parameters={},
    check_ruleset_name="temperature",
)

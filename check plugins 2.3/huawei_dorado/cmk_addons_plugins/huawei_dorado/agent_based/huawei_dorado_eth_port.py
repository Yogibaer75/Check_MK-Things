#!/usr/bin/env python3
'''ETH port check'''
# -*- encoding: utf-8; py-indent-offset: 4 -*-

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
from cmk_addons.plugins.huawei_dorado.lib import (
    HuaweiAPIData,
    check_huawei_health,
    discover_huawei_dorado_items,
    parse_huawei_dorado,
)

agent_section_huawei_dorado_eth_port = AgentSection(
    name="huawei_dorado_eth_port",
    parse_function=parse_huawei_dorado,
    parsed_section_name="huawei_dorado_eth_port",
)


def discover_huawei_dorado_eth_port(section: HuaweiAPIData) -> DiscoveryResult:
    """discover one service per port"""
    for key in section.keys():
        if section[key].get("RUNNINGSTATUS") == "11":
            continue
        yield Service(item=key)


def check_huawei_dorado_eth_port(item: str, section: HuaweiAPIData) -> CheckResult:
    """check ETH port state"""
    data = section.get(item)
    if not data:
        return

    state = check_huawei_health(data)
    for key, health in state.items():
        yield Result(state=State(health[1]), summary=f"{key}: {health[0]}")

    msg = f"Location: {data.get('LOCATION')}\n"
    yield Result(state=State(0), notice="empty", details=msg)


check_plugin_huawei_dorado_eth_port = CheckPlugin(
    name="huawei_dorado_eth_port",
    service_name="ETH Port %s",
    sections=["huawei_dorado_eth_port"],
    discovery_function=discover_huawei_dorado_items,
    check_function=check_huawei_dorado_eth_port,
)

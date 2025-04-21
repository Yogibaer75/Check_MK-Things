#!/usr/bin/env python3
"""Dell ME4 volume statistics check"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2


from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    State,
    render,
)
from cmk_addons.plugins.dell_powervault_me4.lib import parse_dell_powervault_me4

agent_section_dell_powervault_me4_volume_statistics = AgentSection(
    name="dell_powervault_me4_volume_statistics",
    parse_function=parse_dell_powervault_me4,
)


def discovery_dell_powervault_me4_volume_statistics(section) -> DiscoveryResult:
    """for every volume a check is discovered"""
    for item in section:
        yield Service(item=item)


def check_dell_powervault_me4_volume_statistics(
    item: str, params, section
) -> CheckResult:
    """generate volume statistics counters"""
    data = section.get(item, {})
    if not data:
        return
    sas_percent = data.get("percent-tier-sas")
    sata_percent = data.get("percent-tier-sata")
    ssd_percent = data.get("percent-tier-ssd")
    iops = data.get("iops")
    bytespersecond = data.get("bytes-per-second-numeric")
    message = f"Usage SSD: {ssd_percent}%, SAS {sas_percent}%, SATA {sata_percent}%, \
                IOPS {iops}/s, Bytes {render.bytes(bytespersecond)}/s"

    yield Metric("ssd_usage", ssd_percent)
    yield Metric("sas_usage", sas_percent)
    yield Metric("sata_usage", sata_percent)
    yield Metric("iops", iops)
    yield Metric("bytes", bytespersecond)
    yield Result(state=State(0), summary=message)


check_plugin_dell_powervault_me4_volume_statistics = CheckPlugin(
    name="dell_powervault_me4_volume_statistics",
    service_name="Volume Stats %s",
    sections=["dell_powervault_me4_volume_statistics"],
    check_default_parameters={
        "vol_state": 0,
    },
    discovery_function=discovery_dell_powervault_me4_volume_statistics,
    check_function=check_dell_powervault_me4_volume_statistics,
    check_ruleset_name="dell_powervault_me4_volume_statistics",
)

#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# Example output from agent
# <<<windows_dedup:sep(58)>>>
# Volume          : I:
# Enabled         : True
# Capacity        : 24999861673943	capacity
# FreeSpace       : 19474521546752	Compute from capacity - real_capacity
# UsedSpace       : 5525340127232	real_capacity
# UnoptimizedSize : 23045933661347	virtual_capacity
# SavedSpace      : 17520593534115
# SavingsRate     : 76

import time
from typing import Any, Mapping

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    State,
    StringTable,
    get_value_store,
    render,
)
from cmk.plugins.lib.df import FILESYSTEM_DEFAULT_PARAMS, df_check_filesystem_single

Section = Mapping[str, Any]


def parse_windows_dedup(string_table: StringTable) -> Section:
    """Parse agent output into dictionary"""
    data = {}
    last_volume = False
    for line in string_table:
        name = line[0].strip()
        value = ":".join(line[1:]).strip()
        if last_volume and name != "Volume":
            data[last_volume][name] = value
        if name == "Volume":
            last_volume = value
            data[last_volume] = {}
    return data


agent_section_windows_patch_day = AgentSection(
    name="windows_dedup",
    parse_function=parse_windows_dedup,
    parsed_section_name="windows_dedup",
)


def discover_windows_dedup(section: Section) -> DiscoveryResult:
    """One service for every volume with dedup enabled"""
    for n, v in section.items():
        if v.get("Enabled") == "True":
            yield Service(item=n)


def check_windows_dedup(
    item: str, params: Mapping[str, Any], section: Section
) -> CheckResult:
    """Check the deduplication status with integrated df check"""

    data = section.get(item)
    if not data:
        return

    capacity = int(data["Capacity"])
    real_capacity = int(data["UsedSpace"])
    virtual_capacity = int(data["UnoptimizedSize"])
    avail_capacity = capacity - real_capacity
    provisioning = 100.0 * virtual_capacity / capacity
    dedup_savings = float(data["SavingsRate"])
    mb = 1024 * 1024
    yield from df_check_filesystem_single(
        value_store=get_value_store(),
        mountpoint=item,
        filesystem_size=capacity / mb,
        free_space=avail_capacity / mb,
        reserved_space=0,
        inodes_total=None,
        inodes_avail=None,
        params=params,
        this_time=time.time(),
    )

    infotext = (
        f"raw data space: {render.bytes(virtual_capacity)}, "
        f"provisioned space {provisioning:.1f}%, "
        f"dedup savings {dedup_savings:.1f}%"
    )

    yield Result(
        state=State.OK,
        summary=infotext,
    )

    yield Metric("uncommitted", virtual_capacity)
    yield Metric("provisioning", provisioning)
    yield Metric("savings", dedup_savings, boundaries=(0, 100))


check_plugin_windows_patch_day = CheckPlugin(
    name="windows_dedup",
    service_name="Dedup Volume %s",
    check_ruleset_name="filesystem",
    sections=["windows_dedup"],
    check_default_parameters=FILESYSTEM_DEFAULT_PARAMS,
    discovery_function=discover_windows_dedup,
    check_function=check_windows_dedup,
)

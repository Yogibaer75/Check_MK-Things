#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# ported to API v4 by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

import time
from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    State,
    get_value_store,
    render,
)
from cmk.plugins.lib.cpu_util import check_cpu_util  # type: ignore[import]
from cmk.plugins.lib.memory import check_element  # type: ignore[import]
from cmk.plugins.prism_v4.lib_v4 import check_io, CONTROLLER_IO_KEYS, first_value

Section = Mapping[str, Any]

_MEM_KEYS = ("hypervisorMemoryUsagePpm", "aggregateHypervisorMemoryUsagePpm")


def _avg_io_size_bytes(stats: Section, bandwidth_key: str, iops_key: str) -> float:
    """Average I/O size, API v4 has no average size for hosts, so derive it from
    bandwidth (kB/s) and IOPS"""
    iops = float(stats.get(iops_key) or 0)
    if not iops:
        return 0.0
    return float(stats.get(bandwidth_key) or 0) * 1000 / iops


def discovery_prism_host_stats_v4(section: Section) -> DiscoveryResult:
    if section.get("controllerAvgIoLatencyUsecs") is not None:
        yield Service()


def check_prism_host_stats_v4(section: Section) -> CheckResult:
    if not section:
        return

    avg_latency = int(section.get("controllerAvgIoLatencyUsecs", 0))
    avg_read_lat = int(section.get("controllerAvgReadIoLatencyUsecs", 0))
    avg_write_lat = int(section.get("controllerAvgWriteIoLatencyUsecs", 0))
    avg_read_bytes = _avg_io_size_bytes(
        section, "controllerReadIoBandwidthKbps", "controllerNumReadIops"
    )
    avg_write_bytes = _avg_io_size_bytes(
        section, "controllerWriteIoBandwidthKbps", "controllerNumWriteIops"
    )

    yield Result(
        state=State.OK,
        summary=f"is {render.bytes(avg_read_bytes)} read and {render.bytes(avg_write_bytes)} write",
    )
    yield Metric("avg_latency", avg_latency)
    yield Metric("avg_read_lat", avg_read_lat)
    yield Metric("avg_write_lat", avg_write_lat)
    yield Metric("avg_read_bytes", avg_read_bytes)
    yield Metric("avg_write_bytes", avg_write_bytes)
    yield from check_io(section, CONTROLLER_IO_KEYS)


check_plugin_prism_host_stats_v4 = CheckPlugin(
    name="prism_host_stats_v4",
    service_name="NTNX I/O",
    sections=["prism_host_stats_v4"],
    discovery_function=discovery_prism_host_stats_v4,
    check_function=check_prism_host_stats_v4,
)


def discovery_prism_host_stats_cpu_v4(
    section_prism_host_v4: Section | None, section_prism_host_stats_v4: Section | None
) -> DiscoveryResult:
    if section_prism_host_stats_v4 and section_prism_host_stats_v4.get("hypervisorCpuUsagePpm"):
        yield Service()


def check_prism_host_stats_cpu_v4(
    params: Mapping[str, Any],
    section_prism_host_v4: Section | None,
    section_prism_host_stats_v4: Section | None,
) -> CheckResult:
    if not section_prism_host_stats_v4:
        return
    host = section_prism_host_v4 or {}

    num_sockets = int(host.get("numberOfCpuSockets", 0))
    num_cores = int(host.get("numberOfCpuCores", 0))
    num_threads = int(host.get("numberOfCpuThreads", 0))
    hz_capacity = int(section_prism_host_stats_v4.get("cpuCapacityHz", 0))
    cpu_usage_perc = int(section_prism_host_stats_v4.get("hypervisorCpuUsagePpm", 0)) / 10000.0

    yield from check_cpu_util(
        util=cpu_usage_perc,
        params=params,
        value_store=get_value_store(),
        this_time=time.time(),
    )
    yield Result(
        state=State.OK,
        notice=f"{render.frequency(hz_capacity / 100 * cpu_usage_perc)}/{render.frequency(hz_capacity)}",
    )
    yield Result(state=State.OK, notice=f"Sockets: {num_sockets}")
    if num_sockets:
        yield Result(state=State.OK, notice=f"Cores/socket: {int(num_cores / num_sockets)}")
    yield Result(state=State.OK, notice=f"Threads: {num_threads}")


check_plugin_prism_host_stats_cpu_v4 = CheckPlugin(
    name="prism_host_stats_cpu_v4",
    service_name="NTNX CPU",
    sections=["prism_host_v4", "prism_host_stats_v4"],
    check_default_parameters={},
    discovery_function=discovery_prism_host_stats_cpu_v4,
    check_function=check_prism_host_stats_cpu_v4,
    check_ruleset_name="prism_host_cpu",
)


def discovery_prism_host_stats_mem_v4(
    section_prism_host_v4: Section | None, section_prism_host_stats_v4: Section | None
) -> DiscoveryResult:
    if section_prism_host_stats_v4 and first_value(section_prism_host_stats_v4, *_MEM_KEYS):
        yield Service()


def check_prism_host_stats_mem_v4(
    params: Mapping[str, Any],
    section_prism_host_v4: Section | None,
    section_prism_host_stats_v4: Section | None,
) -> CheckResult:
    if not section_prism_host_stats_v4:
        return

    mem_total = int(
        first_value(section_prism_host_stats_v4, "memoryCapacityBytes")
        or (section_prism_host_v4 or {}).get("memorySizeBytes", 0)
    )
    mem_usage = int(first_value(section_prism_host_stats_v4, *_MEM_KEYS) or 0) / 10000.0
    mem_usage_bytes = mem_total / 100 * mem_usage

    yield from check_element(
        "Usage",
        mem_usage_bytes,
        mem_total,
        ("perc_used", params["levels_upper"]),
        metric_name="mem_used",
    )
    yield Metric("mem_total", mem_total)


check_plugin_prism_host_stats_mem_v4 = CheckPlugin(
    name="prism_host_stats_mem_v4",
    service_name="NTNX Memory",
    sections=["prism_host_v4", "prism_host_stats_v4"],
    check_default_parameters={
        "levels_upper": (80.0, 90.0),
    },
    discovery_function=discovery_prism_host_stats_mem_v4,
    check_function=check_prism_host_stats_mem_v4,
    check_ruleset_name="prism_host_mem",
)

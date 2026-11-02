#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# ported to API v4 by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v1 import check_levels as check_levels_v1
from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    State,
    render,
)
from cmk.plugins.lib.memory import check_element  # type: ignore[import]
from cmk.plugins.prism_v4.lib_v4 import check_io, IOKeys

Section = Mapping[str, Any]

_VM_IO_KEYS = IOKeys(
    read_iops="controllerNumReadIops",
    write_iops="controllerNumWriteIops",
    read_kbps="controllerReadIoBandwidthKbps",
    write_kbps="controllerWriteIoBandwidthKbps",
    read_latency_us="controllerAvgReadIoLatencyMicros",
    write_latency_us="controllerAvgWriteIoLatencyMicros",
)


def _is_running(vm: Section | None) -> bool:
    return str((vm or {}).get("powerState", "")).lower() == "on"


def discovery_prism_vm_stats_v4(
    section_prism_vm_v4: Section | None, section_prism_vm_stats_v4: Section | None
) -> DiscoveryResult:
    if section_prism_vm_stats_v4 and section_prism_vm_stats_v4.get(
        "controllerAvgIoLatencyMicros"
    ):
        yield Service()


def check_prism_vm_stats_v4(
    section_prism_vm_v4: Section | None, section_prism_vm_stats_v4: Section | None
) -> CheckResult:
    if not section_prism_vm_stats_v4:
        return

    if not _is_running(section_prism_vm_v4):
        yield Result(state=State.OK, summary="VM not running no I/O check possible")
        return

    data = section_prism_vm_stats_v4
    avg_latency = int(data.get("controllerAvgIoLatencyMicros", 0))
    avg_read_lat = int(data.get("controllerAvgReadIoLatencyMicros", 0))
    avg_write_lat = int(data.get("controllerAvgWriteIoLatencyMicros", 0))
    avg_read_bytes = int(data.get("controllerAvgReadIoSizeKb", 0))
    avg_write_bytes = int(data.get("controllerAvgWriteIoSizeKb", 0))

    message = f"is {render.bytes(avg_read_bytes * 1000)} read and {render.bytes(avg_write_bytes * 1000)} write"
    yield Result(state=State.OK, summary=message)
    yield Metric("avg_latency", avg_latency)
    yield Metric("avg_read_lat", avg_read_lat)
    yield Metric("avg_write_lat", avg_write_lat)
    yield Metric("avg_read_bytes", avg_read_bytes * 1000)
    yield Metric("avg_write_bytes", avg_write_bytes * 1000)
    yield from check_io(data, _VM_IO_KEYS)

    if (user_bytes := data.get("controllerUserBytes")) is not None:
        yield Result(state=State.OK, summary=f"Disk usage: {render.bytes(int(user_bytes))}")
        yield Metric("prism_vm_disk_used", int(user_bytes))


check_plugin_prism_vm_stats_v4 = CheckPlugin(
    name="prism_vm_stats_v4",
    service_name="NTNX I/O",
    sections=["prism_vm_v4", "prism_vm_stats_v4"],
    discovery_function=discovery_prism_vm_stats_v4,
    check_function=check_prism_vm_stats_v4,
)


def discovery_prism_vm_stats_cpu_v4(
    section_prism_vm_v4: Section | None, section_prism_vm_stats_v4: Section | None
) -> DiscoveryResult:
    if section_prism_vm_stats_v4 and section_prism_vm_stats_v4.get("hypervisorCpuReadyTimePpm"):
        yield Service()


def check_prism_vm_stats_cpu_v4(
    params: Mapping[str, Any],
    section_prism_vm_v4: Section | None,
    section_prism_vm_stats_v4: Section | None,
) -> CheckResult:
    if not section_prism_vm_stats_v4:
        return

    if not _is_running(section_prism_vm_v4):
        yield Result(state=State.OK, summary="VM not running no CPU check possible")
        return

    cpu_ready = int(section_prism_vm_stats_v4.get("hypervisorCpuReadyTimePpm", 0)) / 10000.0
    cpu_usage = int(section_prism_vm_stats_v4.get("hypervisorCpuUsagePpm", 0)) / 10000.0

    yield from check_levels_v1(
        value=cpu_usage,
        metric_name="cpu_usage",
        levels_upper=params.get("levels", (None, None)),
        render_func=render.percent,
        label="CPU usage",
        boundaries=(0, 100),
    )
    yield from check_levels_v1(
        value=cpu_ready,
        metric_name="cpu_ready",
        levels_upper=params.get("levels_rdy", (None, None)),
        render_func=render.percent,
        label="CPU ready",
        boundaries=(0, 100),
    )


check_plugin_prism_vm_stats_cpu_v4 = CheckPlugin(
    name="prism_vm_stats_cpu_v4",
    service_name="NTNX CPU",
    sections=["prism_vm_v4", "prism_vm_stats_v4"],
    check_default_parameters={"levels": (80.0, 90.0), "levels_rdy": (5.0, 10.0)},
    discovery_function=discovery_prism_vm_stats_cpu_v4,
    check_function=check_prism_vm_stats_cpu_v4,
    check_ruleset_name="prism_vm_cpu",
)


def discovery_prism_vm_stats_mem_v4(
    section_prism_vm_v4: Section | None, section_prism_vm_stats_v4: Section | None
) -> DiscoveryResult:
    if section_prism_vm_stats_v4 and section_prism_vm_stats_v4.get("guestMemoryUsagePpm"):
        yield Service()


def check_prism_vm_stats_mem_v4(
    params: Mapping[str, Any],
    section_prism_vm_v4: Section | None,
    section_prism_vm_stats_v4: Section | None,
) -> CheckResult:
    if not section_prism_vm_stats_v4:
        return

    if not _is_running(section_prism_vm_v4):
        yield Result(state=State.OK, summary="VM not running no memory check possible")
        return

    mem_total = int((section_prism_vm_v4 or {}).get("memorySizeBytes", 0))
    memory_usage_ppm = section_prism_vm_stats_v4.get("guestMemoryUsagePpm")
    if not mem_total or memory_usage_ppm is None:
        yield Result(state=State.OK, summary="No memory usage data available")
        return

    yield from check_element(
        "Usage",
        mem_total * int(memory_usage_ppm) / 10**6,
        mem_total,
        ("perc_used", params["levels_upper"]),
        metric_name="mem_used",
    )
    yield Metric("mem_total", mem_total)


check_plugin_prism_vm_stats_mem_v4 = CheckPlugin(
    name="prism_vm_stats_mem_v4",
    service_name="NTNX Memory",
    sections=["prism_vm_v4", "prism_vm_stats_v4"],
    check_default_parameters={
        "levels_upper": (80.0, 90.0),
    },
    discovery_function=discovery_prism_vm_stats_mem_v4,
    check_function=check_prism_vm_stats_mem_v4,
    check_ruleset_name="prism_vm_memory",
)

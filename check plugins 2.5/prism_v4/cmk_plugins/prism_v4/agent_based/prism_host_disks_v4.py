#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# ported to API v4 by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

from collections.abc import Iterable, Mapping
from typing import Any

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    render,
    Result,
    Service,
    State,
)
from cmk.plugins.prism_v4.lib_v4 import check_io, IOKeys

Section = Mapping[str, Mapping[str, Any]]

_DISK_IO_KEYS = IOKeys(
    read_iops="diskReadIops",
    write_iops="diskWriteIops",
    read_kbps="diskReadIoBandwidthkbps",
    write_kbps="diskWriteIoBandwidthkbps",
)

_MOUNT_STATES = {
    True: "disk is mounted",
    False: "disk is not mounted",
}


# flags of diskAdvanceConfig which indicate a (coming) problem with the disk
_PROBLEM_FLAGS = (
    ("isUnhealthy", "unhealthy"),
    ("isSuspectedUnhealthy", "suspected unhealthy"),
    ("isErrorFoundInLog", "errors found in log"),
    ("isUnderDiagnosis", "under diagnosis"),
    ("isMarkedForRemoval", "marked for removal"),
)


def _disk_problems(data: Mapping[str, Any], planned_outage: bool) -> Iterable[tuple[State, str]]:
    config = data.get("diskAdvanceConfig", {})
    if config.get("isOnline") is False:
        # an offline disk is expected during a planned outage
        yield (State.WARN if planned_outage else State.CRIT), "offline"
    if (status := data.get("status", "NORMAL")) != "NORMAL":
        yield State.WARN, f"status {status}"
    for flag, text in _PROBLEM_FLAGS:
        if config.get(flag):
            yield State.WARN, text


def discovery_prism_host_disks_v4(section: Section) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_prism_host_disks_v4(
    item: str, params: Mapping[str, Any], section: Section
) -> CheckResult:
    if not (data := section.get(item)):
        return

    config = data.get("diskAdvanceConfig", {})
    mounted = bool(config.get("isMounted"))
    planned_outage = bool(config.get("isPlannedOutage"))
    yield Result(state=State.OK, summary=f"Model: {data.get('model')}")
    yield Result(state=State.OK, summary=f"Serial: {data.get('serialNumber')}")

    problems = list(_disk_problems(data, planned_outage))
    if not problems:
        yield Result(state=State.OK, summary="State: healthy")
    for state, text in problems:
        yield Result(state=state, summary=f"State: {text}")
    if planned_outage:
        yield Result(state=State.OK, summary="Planned outage")
    if config.get("isDataMigrated"):
        yield Result(state=State.OK, notice="Data is migrated off the disk")

    target_state = params.get("mounted", True)
    if mounted is target_state:
        yield Result(state=State.OK, summary=f"Mount state: {_MOUNT_STATES[mounted]}")
    else:
        yield Result(
            state=State.WARN,
            summary=f"Mount state: {_MOUNT_STATES[mounted]} - expected: {_MOUNT_STATES[target_state]}",
        )

    if not (stats := data.get("stats")):
        return
    if (usage_ppm := stats.get("diskUsagePpm")) is not None:
        used_percent = int(usage_ppm) / 10000
        yield Result(state=State.OK, summary=f"Used: {render.percent(used_percent)}")
        yield Metric("fs_used_percent", used_percent, boundaries=(0, 100))
    yield from check_io(stats, _DISK_IO_KEYS, notice_only=True)
    if (latency := stats.get("diskAvgIoLatencyMicrosec")) is not None:
        yield Result(state=State.OK, notice=f"Latency: {render.timespan(int(latency) / 1000000)}")
        yield Metric("disk_latency", int(latency) / 1000000)


check_plugin_prism_host_disks_v4 = CheckPlugin(
    name="prism_host_disks_v4",
    service_name="NTNX HW Disk %s",
    sections=["prism_host_disks_v4"],
    check_default_parameters={"mounted": True},
    discovery_function=discovery_prism_host_disks_v4,
    check_function=check_prism_host_disks_v4,
    check_ruleset_name="prism_host_disks",
)

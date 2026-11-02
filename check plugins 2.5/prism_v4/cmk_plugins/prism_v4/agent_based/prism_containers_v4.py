#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# ported to API v4 by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

from collections.abc import Mapping
from contextlib import suppress
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    GetRateError,
    Metric,
    Result,
    Service,
    State,
    StringTable,
    get_value_store,
)
from cmk.plugins.lib.df import FILESYSTEM_DEFAULT_PARAMS, df_check_filesystem_single  # type: ignore[import]
from cmk.plugins.prism_v4.lib_v4 import check_io, first_value, IOKeys, parse_by_name

Section = Mapping[str, Mapping[str, Any]]

# container stats use other spellings than host and cluster stats
_CONTAINER_IO_KEYS = IOKeys(
    read_iops="controllerNumReadIops",
    write_iops="controllerNumWriteIops",
    read_kbps="controllerReadIoBandwidthkBps",
    write_kbps="controllerWriteIoBandwidthkBps",
    read_latency_us="controllerAvgReadIoLatencyuSecs",
    write_latency_us="controllerAvgWriteIoLatencyuSecs",
)


def parse_prism_containers_v4(string_table: StringTable) -> Section:
    return parse_by_name(string_table)


agent_section_prism_storage_containers_v4 = AgentSection(
    name="prism_storage_containers_v4",
    parse_function=parse_prism_containers_v4,
)


def discovery_prism_containers_v4(section: Section) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def _capacity_and_free(data: Mapping[str, Any]) -> tuple[float, float] | None:
    stats = data.get("stats") or {}
    capacity = first_value(stats, "storageCapacityBytes")
    if capacity is None:
        capacity = data.get("maxCapacityBytes")
    free = first_value(stats, "storageFreeBytes", "freeStorageBytes")
    if (
        free is None
        and capacity is not None
        and (used := first_value(stats, "storageUsageBytes")) is not None
    ):
        free = float(capacity) - float(used)
    if capacity is None or free is None:
        return None
    return float(capacity), float(free)


def check_prism_containers_v4(
    item: str, params: Mapping[str, Any], section: Section
) -> CheckResult:
    if not (data := section.get(item)):
        return

    if (usage := _capacity_and_free(data)) is None:
        yield Result(state=State.UNKNOWN, summary="No usage statistics available")
        return
    capacity, freebytes = usage

    with suppress(GetRateError):
        yield from df_check_filesystem_single(
            get_value_store(),
            item,
            capacity / 1024**2,
            freebytes / 1024**2,
            0,
            None,
            None,
            params=params,
        )

    dedupratio = first_value(
        data.get("stats") or {},
        "dataReductionDedupSavingRatioPpm",
        "dataReductionDedupRatioPpm",
    )
    if data.get("onDiskDedup", "OFF") != "OFF" and dedupratio not in (None, -1):
        dedup_rate = float(dedupratio) / 1000000.0
        yield Metric("dedup_ratio", dedup_rate)
        yield Result(state=State.OK, summary=f"Dedup Ratio: {dedup_rate:.2f}")

    if stats := data.get("stats"):
        yield from check_io(stats, _CONTAINER_IO_KEYS, notice_only=True)


check_plugin_prism_containers_v4 = CheckPlugin(
    name="prism_containers_v4",
    service_name="NTNX Container %s",
    sections=["prism_storage_containers_v4"],
    check_default_parameters=FILESYSTEM_DEFAULT_PARAMS,
    discovery_function=discovery_prism_containers_v4,
    check_function=check_prism_containers_v4,
    check_ruleset_name="filesystem",
)

#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# ported to API v4 by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

from collections.abc import Mapping
from contextlib import suppress
from typing import Any

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    GetRateError,
    Result,
    Service,
    State,
    get_value_store,
    render,
)
from cmk.plugins.lib.df import FILESYSTEM_DEFAULT_PARAMS, df_check_filesystem_single  # type: ignore[import]

Section = Mapping[str, Any]
DiskSection = Mapping[str, Mapping[str, Any]]


def _tier_usage(disks: DiskSection) -> dict[str, tuple[float, float]]:
    """Sum up capacity and free bytes of the disks per tier (SSD or SAS/SATA)

    API v4 has no tier statistics for hosts anymore, but every disk knows its tier."""
    tiers = {"SAS": (0.0, 0.0), "SSD": (0.0, 0.0)}
    for disk in disks.values():
        stats = disk.get("stats") or {}
        tier = "SSD" if str(disk.get("storageTier", "")).startswith("SSD") else "SAS"
        total, free = tiers[tier]
        tiers[tier] = (
            total + float(stats.get("diskCapacityBytes") or 0),
            free + float(stats.get("diskFreeBytes") or 0),
        )
    return tiers


def discovery_prism_host_usage_v4(
    section_prism_host_stats_v4: Section | None, section_prism_host_disks_v4: DiskSection | None
) -> DiscoveryResult:
    if section_prism_host_stats_v4 and section_prism_host_stats_v4.get("storageCapacityBytes"):
        yield Service(item="Capacity")


def check_prism_host_usage_v4(
    item: str,
    params: Mapping[str, Any],
    section_prism_host_stats_v4: Section | None,
    section_prism_host_disks_v4: DiskSection | None,
) -> CheckResult:
    if not section_prism_host_stats_v4:
        return

    total_bytes = float(section_prism_host_stats_v4.get("storageCapacityBytes", 0))
    if (free := section_prism_host_stats_v4.get("freePhysicalStorageBytes")) is not None:
        free_bytes = float(free)
    else:
        free_bytes = total_bytes - float(section_prism_host_stats_v4.get("storageUsageBytes", 0))

    with suppress(GetRateError):
        yield from df_check_filesystem_single(
            get_value_store(),
            item,
            total_bytes / 1024**2,
            free_bytes / 1024**2,
            0,
            None,
            None,
            params=params,
        )

    if section_prism_host_disks_v4:
        tiers = _tier_usage(section_prism_host_disks_v4)
        total_sas, free_sas = tiers["SAS"]
        total_ssd, free_ssd = tiers["SSD"]
        message = f"Total SAS: {render.bytes(total_sas)}, Free SAS: {render.bytes(free_sas)}"
        yield Result(state=State.OK, summary=message)
        message = f"Total SSD: {render.bytes(total_ssd)}, Free SSD: {render.bytes(free_ssd)}"
        yield Result(state=State.OK, summary=message)


check_plugin_prism_host_usage_v4 = CheckPlugin(
    name="prism_host_usage_v4",
    service_name="NTNX Storage %s",
    sections=["prism_host_stats_v4", "prism_host_disks_v4"],
    check_default_parameters=FILESYSTEM_DEFAULT_PARAMS,
    discovery_function=discovery_prism_host_usage_v4,
    check_function=check_prism_host_usage_v4,
    check_ruleset_name="filesystem",
)

#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

from collections.abc import Mapping
from contextlib import suppress
from typing import Any

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    get_value_store,
    GetRateError,
    render,
    Result,
    Service,
    State,
)
from cmk.plugins.lib.df import FILESYSTEM_DEFAULT_PARAMS, df_check_filesystem_single  # type: ignore[import]

Section = Mapping[str, Any]


def discovery_prism_cluster_storage_v4(section: Section) -> DiscoveryResult:
    if section.get("storageCapacityBytes"):
        yield Service(item="Cluster")


def check_prism_cluster_storage_v4(
    item: str, params: Mapping[str, Any], section: Section
) -> CheckResult:
    if not (capacity := section.get("storageCapacityBytes")):
        return
    if (free := section.get("freePhysicalStorageBytes")) is None:
        free = float(capacity) - float(section.get("storageUsageBytes", 0))

    # physical capacity of all disks, replication (redundancy factor) is included in the usage
    with suppress(GetRateError):
        yield from df_check_filesystem_single(
            get_value_store(),
            item,
            float(capacity) / 1024**2,
            float(free) / 1024**2,
            0,
            None,
            None,
            params=params,
        )
    if (logical := section.get("logicalStorageUsageBytes")) is not None:
        yield Result(state=State.OK, notice=f"Logical usage: {render.bytes(int(logical))}")


check_plugin_prism_cluster_storage_v4 = CheckPlugin(
    name="prism_cluster_storage_v4",
    service_name="NTNX Storage %s",
    sections=["prism_cluster_stats_v4"],
    discovery_function=discovery_prism_cluster_storage_v4,
    check_function=check_prism_cluster_storage_v4,
    check_default_parameters=FILESYSTEM_DEFAULT_PARAMS,
    check_ruleset_name="filesystem",
)

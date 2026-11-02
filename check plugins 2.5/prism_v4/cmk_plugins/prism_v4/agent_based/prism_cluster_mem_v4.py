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
    Service,
    render,
)
from cmk.plugins.prism_v4.lib_v4 import first_value

Section = Mapping[str, Any]

# clusters only report the aggregated value, keep the plain one in case it shows up
_MEM_KEYS = ("hypervisorMemoryUsagePpm", "aggregateHypervisorMemoryUsagePpm")


def discovery_prism_cluster_mem_v4(section: Section) -> DiscoveryResult:
    if first_value(section, *_MEM_KEYS) is not None:
        yield Service()


def check_prism_cluster_mem_v4(params: Mapping[str, Any], section: Section) -> CheckResult:
    mem_used = first_value(section, *_MEM_KEYS)
    if mem_used is None:
        return

    yield from check_levels_v1(
        int(mem_used) / 10000,
        metric_name="prism_cluster_mem_used",
        levels_upper=params["levels"],
        boundaries=(0.0, 100.0),
        render_func=render.percent,
        label="Total Memory Usage",
    )


check_plugin_prism_cluster_mem_v4 = CheckPlugin(
    name="prism_cluster_mem_v4",
    service_name="NTNX Cluster Memory",
    sections=["prism_cluster_stats_v4"],
    discovery_function=discovery_prism_cluster_mem_v4,
    check_function=check_prism_cluster_mem_v4,
    check_default_parameters={"levels": (70.0, 80.0)},
    check_ruleset_name="prism_cluster_mem",
)

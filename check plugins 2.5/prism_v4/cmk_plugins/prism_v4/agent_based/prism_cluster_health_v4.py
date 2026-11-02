#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import (
    check_levels,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)

Section = Mapping[str, Any]

# cluster operation modes, everything not listed here is WARN
_OPERATION_MODES = {
    "NORMAL": State.OK,
    "READ_ONLY": State.CRIT,
    "STAND_ALONE": State.WARN,
    "OVERRIDE": State.WARN,
    "SWITCH_TO_TWO_NODE": State.WARN,
}


def discovery_prism_cluster_health_v4(
    section_prism_cluster_v4: Section | None, section_prism_cluster_stats_v4: Section | None
) -> DiscoveryResult:
    if (section_prism_cluster_stats_v4 or {}).get("healthCheckScore") is not None or (
        section_prism_cluster_v4 or {}
    ).get("config", {}).get("operationMode"):
        yield Service()


def check_prism_cluster_health_v4(
    params: Mapping[str, Any],
    section_prism_cluster_v4: Section | None,
    section_prism_cluster_stats_v4: Section | None,
) -> CheckResult:
    config = (section_prism_cluster_v4 or {}).get("config", {})

    if (score := (section_prism_cluster_stats_v4 or {}).get("healthCheckScore")) is not None:
        yield from check_levels(
            int(score),
            levels_lower=params.get("levels_lower"),
            metric_name="prism_health_score",
            label="Health score",
            render_func=lambda v: f"{v:.0f}",
            boundaries=(0, 100),
        )

    if (mode := config.get("operationMode")) is not None:
        yield Result(state=_OPERATION_MODES.get(mode, State.WARN), summary=f"Operation mode: {mode}")

    if config.get("isAvailable") is False:
        yield Result(state=State.CRIT, summary="Cluster is not available")


check_plugin_prism_cluster_health_v4 = CheckPlugin(
    name="prism_cluster_health_v4",
    service_name="NTNX Cluster Health",
    sections=["prism_cluster_v4", "prism_cluster_stats_v4"],
    discovery_function=discovery_prism_cluster_health_v4,
    check_function=check_prism_cluster_health_v4,
    check_default_parameters={"levels_lower": ("fixed", (70, 50))},
    check_ruleset_name="prism_cluster_health",
)

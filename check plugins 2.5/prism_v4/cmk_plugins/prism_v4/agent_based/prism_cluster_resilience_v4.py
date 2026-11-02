#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

import re
from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import CheckPlugin, CheckResult, DiscoveryResult, Result, Service, State

Section = Mapping[str, Any]


def render_fault_tolerance(value: str | None) -> str:
    """Make the cluster fault tolerance readable, e.g. CFT_1N_OR_1D -> 1 node or 1 disk"""
    if value and (match := re.fullmatch(r"CFT_(\d+)N_(OR|AND)_(\d+)D", value)):
        nodes, conjunction, disks = match.groups()
        return (
            f"{nodes} node{'s' if nodes != '1' else ''} {conjunction.lower()} "
            f"{disks} disk{'s' if disks != '1' else ''}"
        )
    return str(value)


def discovery_prism_cluster_resilience_v4(section: Section) -> DiscoveryResult:
    if section.get("config", {}).get("faultToleranceState"):
        yield Service()


def check_prism_cluster_resilience_v4(params: Mapping[str, Any], section: Section) -> CheckResult:
    config = section.get("config", {})
    if not (ft_state := config.get("faultToleranceState")):
        return

    current = ft_state.get("currentMaxFaultTolerance")
    desired = ft_state.get("desiredMaxFaultTolerance")
    state_degraded = State(params.get("state_degraded", State.CRIT.value))

    summary = (
        f"Fault tolerance: {current} "
        f"({render_fault_tolerance(ft_state.get('currentClusterFaultTolerance'))})"
    )
    if current is None or desired is None:
        yield Result(state=State.UNKNOWN, summary=f"{summary}, desired: {desired}")
    elif current < desired:
        yield Result(
            state=state_degraded,
            summary=(
                f"{summary}, desired: {desired} "
                f"({render_fault_tolerance(ft_state.get('desiredClusterFaultTolerance'))})"
            ),
        )
    else:
        yield Result(state=State.OK, summary=summary)

    if (minimum := params.get("min_fault_tolerance")) is not None and (
        current is not None and current < minimum
    ):
        yield Result(state=state_degraded, summary=f"Below configured minimum of {minimum}")

    if (redundancy_factor := config.get("redundancyFactor")) is not None:
        yield Result(state=State.OK, summary=f"Redundancy factor: {redundancy_factor}")
    if (awareness := ft_state.get("domainAwarenessLevel")) is not None:
        yield Result(state=State.OK, notice=f"Domain awareness: {awareness}")


check_plugin_prism_cluster_resilience_v4 = CheckPlugin(
    name="prism_cluster_resilience_v4",
    service_name="NTNX Cluster Resilience",
    sections=["prism_cluster_v4"],
    discovery_function=discovery_prism_cluster_resilience_v4,
    check_function=check_prism_cluster_resilience_v4,
    check_default_parameters={"state_degraded": State.CRIT.value},
    check_ruleset_name="prism_cluster_resilience",
)

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
    Service,
    get_value_store,
)
from cmk.plugins.lib.cpu_util import check_cpu_util  # type: ignore[import]

Section = Mapping[str, Any]


def discovery_prism_cluster_cpu_v4(section: Section) -> DiscoveryResult:
    if "hypervisorCpuUsagePpm" in section:
        yield Service()


def check_prism_cluster_cpu_v4(params: Mapping[str, Any], section: Section) -> CheckResult:
    cpu_used = section.get("hypervisorCpuUsagePpm")
    if cpu_used is None:
        return

    yield from check_cpu_util(
        util=int(cpu_used) / 10000,
        params=params,
        value_store=get_value_store(),
        this_time=time.time(),
    )


check_plugin_prism_cluster_cpu_v4 = CheckPlugin(
    name="prism_cluster_cpu_v4",
    service_name="NTNX Cluster CPU",
    sections=["prism_cluster_stats_v4"],
    discovery_function=discovery_prism_cluster_cpu_v4,
    check_function=check_prism_cluster_cpu_v4,
    check_default_parameters={},
    check_ruleset_name="prism_cluster_cpu",
)

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
    Service,
)
from cmk.plugins.prism_v4.lib_v4 import check_io, CONTROLLER_IO_KEYS

Section = Mapping[str, Any]


def _io_bandwidth_kbps(section: Section) -> float | None:
    """Controller bandwidth in kB/s, clusters only report read and write separately"""
    if (total := section.get("controllerIoBandwidthKbps")) is not None:
        return float(total)
    read = section.get("controllerReadIoBandwidthKbps")
    write = section.get("controllerWriteIoBandwidthKbps")
    if read is None and write is None:
        return None
    return float(read or 0) + float(write or 0)


def discovery_prism_cluster_io_v4(section: Section) -> DiscoveryResult:
    if (
        _io_bandwidth_kbps(section) is not None
        and "controllerNumIops" in section
        and "controllerAvgIoLatencyUsecs" in section
    ):
        yield Service()


def _scaled(levels: tuple[float, float] | None, factor: float) -> tuple[float, float] | None:
    return None if levels is None else (levels[0] * factor, levels[1] * factor)


def check_prism_cluster_io_v4(params: Mapping[str, Any], section: Section) -> CheckResult:
    # Levels are configured in MB/s and ms (like the v2 check), the metrics are
    # written in B/s and s to match the units of the metric definitions.
    if (iobw_kbps := _io_bandwidth_kbps(section)) is not None:
        iobw = iobw_kbps / 1000
        yield from check_levels_v1(
            iobw,
            levels_upper=params["io"],
            label="I/O Bandwidth",
            render_func=lambda d: f"{d:.2f} MB/s",
        )
        yield Metric(
            "prism_cluster_iobw", iobw * 1000**2, levels=_scaled(params["io"], 1000**2)
        )

    if (iops := section.get("controllerNumIops")) is not None:
        yield from check_levels_v1(
            int(iops),
            levels_upper=params["iops"],
            metric_name="prism_cluster_iops",
            label="IOPS",
        )

    if (iolatency_raw := section.get("controllerAvgIoLatencyUsecs")) is not None:
        iolatency = int(iolatency_raw) / 1000
        yield from check_levels_v1(
            iolatency,
            levels_upper=params["iolat"],
            label="I/O Latency",
            render_func=lambda d: f"{d:.1f} ms",
        )
        yield Metric(
            "prism_cluster_iolatency", iolatency / 1000, levels=_scaled(params["iolat"], 1 / 1000)
        )

    # read/write split, levels only apply to the totals above
    yield from check_io(section, CONTROLLER_IO_KEYS, notice_only=True)


check_plugin_prism_cluster_io_v4 = CheckPlugin(
    name="prism_cluster_io_v4",
    service_name="NTNX Cluster Controller IO",
    sections=["prism_cluster_stats_v4"],
    discovery_function=discovery_prism_cluster_io_v4,
    check_function=check_prism_cluster_io_v4,
    check_default_parameters={
        "io": (500.0, 1000.0),
        "iops": (10000, 20000),
        "iolat": (500.0, 1000.0),
    },
    check_ruleset_name="prism_cluster_io",
)

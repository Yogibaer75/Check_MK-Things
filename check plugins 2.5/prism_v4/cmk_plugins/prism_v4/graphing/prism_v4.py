#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.graphing.v1 import metrics, perfometers, Title

UNIT_SCORE = metrics.Unit(metrics.DecimalNotation(""), metrics.StrictPrecision(0))

metric_prism_health_score = metrics.Metric(
    name="prism_health_score",
    title=Title("Health score"),
    unit=UNIT_SCORE,
    color=metrics.Color.GREEN,
)

perfometer_prism_health_score = perfometers.Perfometer(
    name="prism_health_score",
    focus_range=perfometers.FocusRange(perfometers.Closed(0), perfometers.Closed(100)),
    segments=["prism_health_score"],
)

metric_prism_vm_disk_used = metrics.Metric(
    name="prism_vm_disk_used",
    title=Title("Used disk space"),
    unit=metrics.Unit(metrics.IECNotation("B")),
    color=metrics.Color.BLUE,
)

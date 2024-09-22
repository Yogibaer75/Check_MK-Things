#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
'''Metric definition for Windows deduplication check'''
# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.graphing.v1 import metrics, Title

metric_dedup_provisioning = metrics.Metric(
    name="provisioning",
    title=Title("Data size in relation to Space"),
    unit=metrics.Unit(metrics.DecimalNotation("%")),
    color=metrics.Color.DARK_CYAN,
)

metric_dedup_savings = metrics.Metric(
    name="savings",
    title=Title("Saved space after dedup"),
    unit=metrics.Unit(metrics.DecimalNotation("%")),
    color=metrics.Color.CYAN,
)

metric_dedup_uncommitted = metrics.Metric(
    name="uncommitted",
    title=Title("Raw data size"),
    unit=metrics.Unit(metrics.IECNotation("B")),
    color=metrics.Color.BROWN,
)

# windows_dedup_perfvarnames = ["fs_size", "growth", "trend",
#                               "provisining", "uncommitted", "savings"]

# check_metrics["check_mk-windows_dedup"] = {
#     "~(?!%s).*$" % "|".join(df_basic_perfvarnames) : { "name"  : "fs_used", "scale" : MB },
#     "fs_size"    : { "scale" : MB },
#     "trend"      : { "name"  : "fs_trend", "scale" : MB / 86400.0 },
#     "uncommitted" : { "name" : "uncommitted" },
#     "provisining" : { "name" : "provisining" },
#     "savings"     : { "name" : "savings" },
# }

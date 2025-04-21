#!/usr/bin/env python3

# (c) Jens Kühnel <fail2ban-checkmk@jens.kuehnel.org> 2021
#
# Information about fail2ban check_mk module see:
# https://github.com/JensKuehnel/fail2ban-check-mk
#
# License: GNU General Public License v2

from cmk.graphing.v1 import metrics, Title, graphs

metric_fail2ban_current_failed = metrics.Metric(
    name="current_failed",
    title=Title("Current failed"),
    unit=metrics.Unit(metrics.DecimalNotation(""), metrics.StrictPrecision(0)),
    color=metrics.Color.BLUE,
)

metric_fail2ban_current_banned = metrics.Metric(
    name="current_banned",
    title=Title("Current banned"),
    unit=metrics.Unit(metrics.DecimalNotation(""), metrics.StrictPrecision(0)),
    color=metrics.Color.RED,
)

metric_fail2ban_total_failed = metrics.Metric(
    name="total_failed",
    title=Title("Total failed"),
    unit=metrics.Unit(metrics.DecimalNotation(""), metrics.StrictPrecision(0)),
    color=metrics.Color.DARK_BLUE,
)

metric_fail2ban_total_banned = metrics.Metric(
    name="total_banned",
    title=Title("Total banned"),
    unit=metrics.Unit(metrics.DecimalNotation(""), metrics.StrictPrecision(0)),
    color=metrics.Color.DARK_RED,
)

graph_info_fail2ban_current = graphs.Graph(
    name="fail2ban_current",
    title=Title("Fail2ban current"),
    simple_lines=[
        "current_failed",
        "current_banned",
    ],
)

graph_info_fail2ban_total = graphs.Graph(
    name="fail2ban_total",
    title=Title("Fail2ban total"),
    simple_lines=[
        "total_failed",
        "total_banned",
    ],
)

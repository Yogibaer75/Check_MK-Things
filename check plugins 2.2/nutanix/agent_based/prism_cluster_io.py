#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.
from typing import Any, Dict, Mapping

from cmk.base.plugins.agent_based.agent_based_api.v1 import check_levels, register, Service
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import CheckResult, DiscoveryResult

Section = Dict[str, Mapping[str, Any]]


def discovery_prism_cluster_io(section: Section) -> DiscoveryResult:
    stat_keys = (
        "controller_io_bandwidth_kBps",
        "controller_num_iops",
        "controller_avg_io_latency_usecs",
    )
    if {*stat_keys} <= section.get("stats", {}).keys():
        yield Service()


def check_prism_cluster_io(params: Mapping[str, Any], section: Section) -> CheckResult:
    iobw_used = section.get("stats", {}).get("controller_io_bandwidth_kBps")
    if iobw_used:
        iobw_usage = int(iobw_used) / 10000
        yield from check_levels(
            iobw_usage,
            levels_upper=params["io"],
            metric_name="prism_cluster_iobw",
            label="I/O Bandwidth",
            render_func=lambda d: f"{d:.2f} MB/s",
        )

    iops_used = section.get("stats", {}).get("controller_num_iops")
    if iops_used:
        iops_usage = int(iops_used) / 10000
        yield from check_levels(
            iops_usage,
            levels_upper=params["iops"],
            metric_name="prism_cluster_iops",
            label="IOPS",
        )

    iolatency_raw = section.get("stats", {}).get("controller_avg_io_latency_usecs")
    if iolatency_raw:
        iolatency = int(iolatency_raw) / 1000

        yield from check_levels(
            iolatency,
            levels_upper=params["iolat"],
            metric_name="prism_cluster_iolatency",
            label="I/O Latency",
            render_func=lambda d: f"{d:.1f} ms",
        )


register.check_plugin(
    name="prism_cluster_io",
    service_name="NTNX Cluster Controller IO",
    sections=["prism_info"],
    discovery_function=discovery_prism_cluster_io,
    check_function=check_prism_cluster_io,
    check_default_parameters={
        "io": (500.0, 1000.0),
        "iops": (10000.0, 20000.0),
        "iolat": (500.0, 1000.0),
    },
    check_ruleset_name="prism_cluster_io",
)

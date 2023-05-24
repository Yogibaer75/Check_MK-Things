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

from cmk.base.plugins.agent_based.agent_based_api.v1 import check_levels, register, render, Service
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import CheckResult, DiscoveryResult

Section = Dict[str, Mapping[str, Any]]


def discovery_prism_info_mem(section: Section) -> DiscoveryResult:
    if "hypervisor_memory_usage_ppm" in section.get("stats", {}):
        yield Service()


def check_prism_info_mem(params: Mapping[str, Any], section: Section) -> CheckResult:
    mem_used = section.get("stats", {}).get("hypervisor_memory_usage_ppm")
    if mem_used is None:
        return

    check_params = tuple

    if "levels_upper" in params.keys():
        check_params = params["levels_upper"]
    else:
        check_params = params["levels"]

    mem_usage = int(mem_used) / 10000

    yield from check_levels(
        mem_usage,
        metric_name="prism_cluster_mem_used",
        levels_upper=check_params,
        boundaries=(0.0, 100.0),
        render_func=render.percent,
        label="Total Memory Usage",
    )


register.check_plugin(
    name="prism_info_mem",
    service_name="NTNX Cluster Memory",
    sections=["prism_info"],
    discovery_function=discovery_prism_info_mem,
    check_function=check_prism_info_mem,
    check_default_parameters={"levels": (70.0, 80.0)},
    check_ruleset_name="prism_cluster_mem",
)

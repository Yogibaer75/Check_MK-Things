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
import time
from typing import Any, Dict, Mapping

from .agent_based_api.v1 import get_value_store, register, Service
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult
from .utils.cpu_util import check_cpu_util

Section = Dict[str, Mapping[str, Any]]


def discovery_prism_cluster_cpu(section: Section) -> DiscoveryResult:
    if "hypervisor_cpu_usage_ppm" in section.get("stats", {}):
        yield Service()


def check_prism_cluster_cpu(params: Mapping[str, Any], section: Section) -> CheckResult:
    cpu_used = section.get("stats", {}).get("hypervisor_cpu_usage_ppm")
    if cpu_used is None:
        return

    cpu_usage = int(cpu_used) / 10000

    yield from check_cpu_util(
        util=cpu_usage,
        params=params,
        value_store=get_value_store(),
        this_time=time.time(),
    )


register.check_plugin(
    name="prism_cluster_cpu",
    service_name="NTNX Cluster CPU",
    sections=["prism_info"],
    discovery_function=discovery_prism_cluster_cpu,
    check_function=check_prism_cluster_cpu,
    check_default_parameters={},
    check_ruleset_name="prism_cluster_cpu",
)

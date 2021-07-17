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

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)

from .agent_based_api.v1 import (
    register,
    Result,
    State,
    Service,
    render,
    Metric,
)


def parse_prism_host_stats(string_table):
    import ast
    parsed = {}
    parsed = ast.literal_eval(string_table[0][0])
    return parsed


register.agent_section(
    name="prism_host_stats",
    parse_function=parse_prism_host_stats,
)


def discovery_prism_host_stats(section) -> DiscoveryResult:
    if "controller_avg_io_latency_usecs" in section:
        yield Service()


def check_prism_host_stats(params, section) -> CheckResult:
    state = 0

    avg_latency = int(section.get("controller_avg_io_latency_usecs"))
    avg_read_lat = int(section.get("controller_avg_read_io_latency_usecs"))
    avg_write_lat = int(section.get("controller_avg_write_io_latency_usecs"))
    avg_read_bytes = int(section.get("controller_avg_read_io_size_kbytes"))
    avg_write_bytes = int(section.get("controller_avg_write_io_size_kbytes"))

    message = f"is {render.bytes(avg_read_bytes * 1000)} read and {render.bytes(avg_write_bytes * 1000)} write"
    yield Result(state=State(state), summary=message)
    yield Metric("avg_latency", avg_latency)
    yield Metric("avg_read_lat", avg_read_lat)
    yield Metric("avg_write_lat", avg_write_lat)
    yield Metric("avg_read_bytes", avg_read_bytes)
    yield Metric("avg_write_bytes", avg_write_bytes)


register.check_plugin(
    name="prism_host_stats",
    service_name="NTNX I/O",
    sections=["prism_host_stats"],
    check_default_parameters={
        'system_state': 0,
    },
    discovery_function=discovery_prism_host_stats,
    check_function=check_prism_host_stats,
    check_ruleset_name="prism_host_stats",
)


def discovery_prism_host_stats_cpu(section) -> DiscoveryResult:
    if "hypervisor_cpu_usage_ppm" in section:
        yield Service()


def check_prism_host_stats_cpu(params, section) -> CheckResult:
    state = 0
    cpu_usage = int(section.get("hypervisor_cpu_usage_ppm")) / 10000.0
    message = f"Usage {cpu_usage:.2f}%"

    yield Result(state=State(state), summary=message)
    yield Metric("cpu_usage", cpu_usage)


register.check_plugin(
    name="prism_host_stats_cpu",
    service_name="NTNX CPU",
    sections=["prism_host_stats"],
    check_default_parameters={
        'system_state': 0,
    },
    discovery_function=discovery_prism_host_stats_cpu,
    check_function=check_prism_host_stats_cpu,
    check_ruleset_name="prism_host_stats",
)


def discovery_prism_host_stats_mem(section) -> DiscoveryResult:
    if "hypervisor_memory_usage_ppm" in section:
        yield Service()


def check_prism_host_stats_mem(params, section) -> CheckResult:
    state = 0
    mem_usage = int(section.get("hypervisor_memory_usage_ppm")) / 10000.0
    message = f"Usage {mem_usage:.2f}%"
    yield Result(state=State(state), summary=message)
    yield Metric("mem_used_percent", mem_usage)


register.check_plugin(
    name="prism_host_stats_mem",
    service_name="NTNX Memory",
    sections=["prism_host_stats"],
    check_default_parameters={
        'system_state': 0,
    },
    discovery_function=discovery_prism_host_stats_mem,
    check_function=check_prism_host_stats_mem,
    check_ruleset_name="prism_host_stats",
)

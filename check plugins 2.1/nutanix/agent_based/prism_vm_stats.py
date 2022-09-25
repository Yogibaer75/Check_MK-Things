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


def parse_prism_vm_stats(string_table):
    import ast
    parsed = {}
    parsed = ast.literal_eval(string_table[0][0])
    return parsed


register.agent_section(
    name="prism_vm_stats",
    parse_function=parse_prism_vm_stats,
)


def discovery_prism_vm_stats(section) -> DiscoveryResult:
    if "controller_avg_io_latency_usecs" in section:
        yield Service()


def check_prism_vm_stats(params, section) -> CheckResult:
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
    name="prism_vm_stats",
    service_name="NTNX I/O",
    sections=["prism_vm_stats"],
    check_default_parameters={
        'system_state': 0,
    },
    discovery_function=discovery_prism_vm_stats,
    check_function=check_prism_vm_stats,
    check_ruleset_name="prism_vm_stats",
)


def discovery_prism_vm_stats_cpu(section) -> DiscoveryResult:
    if "hypervisor.cpu_ready_time_ppm" in section:
        yield Service()


def check_prism_vm_stats_cpu(params, section) -> CheckResult:
    state = 0
    cpu_ready = int(section.get("hypervisor.cpu_ready_time_ppm")) / 10000.0
    cpu_usage = int(section.get("hypervisor_cpu_usage_ppm")) / 10000.0
    message = f"Usage {cpu_usage:.2f}% - CPU ready {cpu_ready:.2f}%"

    yield Result(state=State(state), summary=message)
    yield Metric("cpu_usage", cpu_usage)
    yield Metric("cpu_ready", cpu_ready)


register.check_plugin(
    name="prism_vm_stats_cpu",
    service_name="NTNX CPU",
    sections=["prism_vm_stats"],
    check_default_parameters={
        'system_state': 0,
    },
    discovery_function=discovery_prism_vm_stats_cpu,
    check_function=check_prism_vm_stats_cpu,
    check_ruleset_name="prism_vm_stats",
)


def discovery_prism_vm_stats_mem(section) -> DiscoveryResult:
    if "guest.memory_usage_ppm" in section:
        yield Service()


def check_prism_vm_stats_mem(params, section) -> CheckResult:
    state = 0
    mem_usage_bytes = int(section.get("guest.memory_usage_bytes"))
    if mem_usage_bytes != 0:
        mem_usage = int(section.get("guest.memory_usage_ppm")) / 10000.0
        mem_total = int(
            mem_usage_bytes / mem_usage * 100)
        if mem_total < 500000000:
            mem_total = mem_total * 1024
            mem_usage_bytes = mem_usage_bytes * 1024
        message = f"Usage {mem_usage:.2f}% - {render.bytes(mem_usage_bytes)} from {render.bytes(mem_total)}"

        yield Result(state=State(state), summary=message)
        yield Metric("mem_used", mem_usage_bytes)
        yield Metric("mem_total", mem_total)
        yield Metric("mem_used_percent", mem_usage)
    else:
        yield Result(state=State(state),
                     summary="VM not running no memory check possible")


register.check_plugin(
    name="prism_vm_stats_mem",
    service_name="NTNX Memory",
    sections=["prism_vm_stats"],
    check_default_parameters={
        'system_state': 0,
    },
    discovery_function=discovery_prism_vm_stats_mem,
    check_function=check_prism_vm_stats_mem,
    check_ruleset_name="prism_vm_stats",
)
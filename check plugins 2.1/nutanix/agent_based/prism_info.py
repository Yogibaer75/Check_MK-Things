#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
# ported by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
import time
from typing import Any, Dict, Mapping

from .agent_based_api.v1 import register, Result, Service, State, get_value_store, Metric, check_levels
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, StringTable
from .utils import cpu_util
Section = Dict[Any, Any]


def parse_prism_info(string_table: StringTable) -> Section:
    import ast

    data = ast.literal_eval(string_table[0][0])
    return data


register.agent_section(
    name="prism_info",
    parse_function=parse_prism_info,
)


def discovery_prism_info(section: Section) -> DiscoveryResult:
    if section:
        yield Service()


def check_prism_info(section: Section) -> CheckResult:

    summary = (
        f"Name: {section.get('name')}, "
        f"Version: {section.get('version')}, "
        f"Nodes: {section.get('num_nodes')}, "
        f"ID: {section.get('id')}")

    yield Result(
        state=State.OK,
        summary=summary,
    )


register.check_plugin(
    name="prism_info",
    service_name="NTNX Cluster",
    sections=["prism_info"],
    discovery_function=discovery_prism_info,
    check_function=check_prism_info,
)

### Cluster CPU

register.agent_section(
    name="prism_info_cpu",
    parse_function=parse_prism_info,
)

def discovery_prism_info_cpu(section: Section) -> DiscoveryResult:
    if"hypervisor_cpu_usage_ppm" in section["stats"]:
        yield Service()
    
def check_prism_info_cpu(
    params: Mapping[str, Any], 
    section: Section) -> CheckResult:
   
    yield from cpu_util.check_cpu_util(
        util=int(section["stats"].get("hypervisor_cpu_usage_ppm", 0))/10000,
        params=params,
        value_store=get_value_store(), 
        this_time=time.time()
    )

register.check_plugin(
    name="prism_info_cpu",
    service_name="NTNX Cluster CPU",
    sections=["prism_info"],
    discovery_function=discovery_prism_info_cpu,
    check_function=check_prism_info_cpu,
    check_default_parameters={}
)


### Cluster Memory

register.agent_section(
    name="prism_info_mem",
    parse_function=parse_prism_info,
)

def discovery_prism_info_mem(section: Section) -> DiscoveryResult:
    if"hypervisor_memory_usage_ppm" in section["stats"]:
        yield Service()
    
def check_prism_info_mem(
    params: Mapping[str, Any], 
    section: Section) -> CheckResult:
 
    mem_used = int(section["stats"].get("hypervisor_memory_usage_ppm", 0))/10000  

    state = State.OK   
    if "levels_upper" in params:
        warn, crit = params["levels_upper"]
        if mem_used >= crit:
            state = State.CRIT
        elif mem_used >= warn:
            state = State.WARN

    yield Result(state=state, summary=f"Total Memory: {mem_used:.2f}%")
    yield Metric(
        "prism_cluster_mem_used",
        mem_used,
        levels=params.get("levels_upper", None),
        boundaries=(0.0, 100),        
    )

register.check_plugin(
    name="prism_info_mem",
    service_name="NTNX Cluster Memory",
    sections=["prism_info"],
    discovery_function=discovery_prism_info_mem,
    check_function=check_prism_info_mem,
    check_default_parameters={},
    check_ruleset_name="prism_cluster_mem",
)

### Cluster iobw

register.agent_section(
    name="prism_info_iobw",
    parse_function=parse_prism_info,
)

def discovery_prism_info_iobw(section: Section) -> DiscoveryResult:
    if"controller_io_bandwidth_kBps" in section["stats"]:
        yield Service()
    
def check_prism_info_iobw(
    section: Section) -> CheckResult:
 
    iobw = int(section["stats"].get("controller_io_bandwidth_kBps", 0))/1000 

    yield from check_levels(
        iobw,
        metric_name="prism_cluster_iobw",
        label="Current I/O Bandwidth",
        render_func=lambda d: "%.2f MB/s" % d,
    )  

register.check_plugin(
    name="prism_info_iobw",
    service_name="NTNX Cluster-wide Controller IO B/W",
    sections=["prism_info"],
    discovery_function=discovery_prism_info_iobw,
    check_function=check_prism_info_iobw,

)

### Cluster iops

register.agent_section(
    name="prism_info_iops",
    parse_function=parse_prism_info,
)

def discovery_prism_info_iops(section: Section) -> DiscoveryResult:
    if"controller_num_iops" in section["stats"]:
        yield Service()
    
def check_prism_info_iops(
    section: Section) -> CheckResult:
 
    iops = int(section["stats"].get("controller_num_iops", 0)) 

    yield from check_levels(
        iops,
        metric_name="prism_cluster_iops",
        label="Current IOPS",
#        render_func=lambda d: "%d" % d,
    )  

register.check_plugin(
    name="prism_info_iops",
    service_name="NTNX Cluster-wide Controler IOPS",
    sections=["prism_info"],
    discovery_function=discovery_prism_info_iops,
    check_function=check_prism_info_iops,

)
### Cluster iolatency

register.agent_section(
    name="prism_info_iolatency",
    parse_function=parse_prism_info,
)

def discovery_prism_info_iolatency(section: Section) -> DiscoveryResult:
    if"controller_avg_io_latency_usecs" in section["stats"]:
        yield Service()
    
def check_prism_info_iolatency(
    section: Section) -> CheckResult:
 
    iolatency = int(section["stats"].get("controller_avg_io_latency_usecs", 0))/1000

    yield from check_levels(
        iolatency,
        metric_name="prism_cluster_iolatency",
        label="Current I/O Latency",
        render_func=lambda d: "%.1f ms" % d,
    )  

register.check_plugin(
    name="prism_info_iolatency",
    service_name="NTNX Cluster-wide Controler Latency",
    sections=["prism_info"],
    discovery_function=discovery_prism_info_iolatency,
    check_function=check_prism_info_iolatency,

)
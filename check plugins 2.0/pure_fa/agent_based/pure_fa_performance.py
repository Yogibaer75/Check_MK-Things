#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
# ported by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
import ast
from typing import Any, Dict, Mapping

from .agent_based_api.v1 import register, render, Metric, Result, Service, State
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, StringTable

Section = Dict[str, Mapping[str, Any]]


def parse_pure_fa_performance(string_table: StringTable) -> Section:
    parsed: Section = {}
    parsed = ast.literal_eval(string_table[0][0])[0]
    return parsed


register.agent_section(
    name="pure_fa_performance",
    parse_function=parse_pure_fa_performance,
)


def discovery_pure_fa_performance(section: Section) -> DiscoveryResult:
    if section:
        yield Service()


def check_pure_fa_performance(section: Section) -> CheckResult:
    if not section:
        return

    iops_read = section.get("reads_per_sec", 0) 
    iops_write = section.get("writes_per_sec", 0)
    lat_read = section.get("usec_per_read_op", 0)
    lat_write = section.get("usec_per_write_op", 0)
    input_bytes = section.get("input_per_sec", 0)
    output_bytes = section.get("output_per_sec", 0)
    queue = section.get("queue_depth", 0)

    message = f"is {render.bytes(output_bytes)} read and {render.bytes(input_bytes)} write"
    yield Result(state=State.OK, summary=message)
    yield Metric("iops_read", iops_read)
    yield Metric("iops_write", iops_write)
    yield Metric("lat_read", lat_read)
    yield Metric("lat_write", lat_write)
    yield Metric("input_bytes", input_bytes)
    yield Metric("output_bytes", output_bytes)


register.check_plugin(
    name="pure_fa_performance",
    service_name="Pure Performance",
    sections=["pure_fa_performance"],
    discovery_function=discovery_pure_fa_performance,
    check_function=check_pure_fa_performance,
)

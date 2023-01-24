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


def parse_pure_fa_occ(string_table: StringTable) -> Section:
    parsed: Section = {}
    data = ast.literal_eval(string_table[0][0])
    for element in data:
        parsed.setdefault(element.get("hostname", "unknown"), element)
    return parsed


register.agent_section(
    name="pure_fa_occ",
    parse_function=parse_pure_fa_occ,
)

def discovery_pure_fa_occ(section: Section) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_pure_fa_occ(item: str,section: Section) -> CheckResult:
    data = section.get(item)
    if not data:
        return

    capacity = data.get("capacity")
    provisioned =  data.get("provisioned")
    volumes = data.get("volumes")
    data_reduction = data.get("data_reduction")
    total = data.get("total")
    total_reduction = data.get("total_reduction")
    shared = data.get("shared_space")

    unique_data = total - shared
    free_space = capacity - total

    message = f"{render.bytes(capacity)} Capacity with {render.bytes(shared)} shared and {render.bytes(unique_data)} unique data."
    yield Result(state=State.OK, summary=message)
    yield Metric("capacity", capacity)
    yield Metric("unique_data", unique_data)
    yield Metric("shared_data", shared)
    yield Metric("free_space", free_space)
    yield Metric("provisioned_space", provisioned)
    yield Metric("reduction", total_reduction)


register.check_plugin(
    name="pure_fa_occ",
    service_name="Pure Space %s",
    sections=["pure_fa_occ"],
    discovery_function=discovery_pure_fa_occ,
    check_function=check_pure_fa_occ,
)


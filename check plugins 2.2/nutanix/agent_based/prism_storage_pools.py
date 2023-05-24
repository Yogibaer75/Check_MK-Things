#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
# ported by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
from contextlib import suppress
from typing import Any, Dict, Mapping

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    get_value_store,
    GetRateError,
    register,
    render,
    Result,
    Service,
    State,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, StringTable
from cmk.base.plugins.agent_based.utils.df import df_check_filesystem_single, FILESYSTEM_DEFAULT_PARAMS
from .utils.prism import load_json

Section = Dict[str, Mapping[str, Any]]


def parse_prism_storage_pools(string_table: StringTable) -> Section:
    parsed: Section = {}
    data = load_json(string_table)
    for element in data.get("entities", {}):
        parsed.setdefault(element.get("name", "unknown"), element)
    return parsed


register.agent_section(
    name="prism_storage_pools",
    parse_function=parse_prism_storage_pools,
)


def discovery_prism_storage_pools(section: Section) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_prism_storage_pools(
    item: str, params: Mapping[str, Any], section: Section
) -> CheckResult:
    value_store = get_value_store()
    data = section.get(item)
    if not data:
        return

    das_cap = float(data["usageStats"].get("storage_tier.das-sata.capacity_bytes", 0))
    das_free = float(data["usageStats"].get("storage_tier.das-sata.free_bytes", 0))
    ssd_cap = float(data["usageStats"].get("storage_tier.ssd.capacity_bytes", 0))
    ssd_free = float(data["usageStats"].get("storage_tier.ssd.free_bytes", 0))
    tot_cap = float(data["usageStats"].get("storage.capacity_bytes", 0))
    tot_free = float(data["usageStats"].get("storage.free_bytes", 0))

    with suppress(GetRateError):
        yield from df_check_filesystem_single(
            value_store,
            item,
            tot_cap / 1024**2,
            tot_free / 1024**2,
            0,
            None,
            None,
            params=params,
        )
    if das_cap > 0:
        message = (
            f"SAS/SATA capacity: {render.bytes(das_cap)}, SAS/SATA free: {render.bytes(das_free)}"
        )
        yield Result(state=State(0), summary=message)

    if ssd_cap > 0:
        message = f"SSD capacity: {render.bytes(ssd_cap)}, SSD free: {render.bytes(ssd_free)}"
        yield Result(state=State(0), summary=message)


register.check_plugin(
    name="prism_storage_pools",
    service_name="NTNX Storage %s",
    sections=["prism_storage_pools"],
    check_default_parameters=FILESYSTEM_DEFAULT_PARAMS,
    discovery_function=discovery_prism_storage_pools,
    check_function=check_prism_storage_pools,
    check_ruleset_name="filesystem",
)

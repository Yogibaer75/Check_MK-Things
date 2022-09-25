#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)
from .agent_based_api.v1 import (
    register,
    Service,
    get_value_store,
)
from .utils.df import (
    df_check_filesystem_single,
    FILESYSTEM_DEFAULT_LEVELS,
)


def parse_prism_container(string_table):
    import ast

    parsed = {}
    data = ast.literal_eval(string_table[0][0])
    for element in data.get("entities"):
        parsed.setdefault(element.get("name", "unknown"), element)
    return parsed


register.agent_section(
    name="prism_containers",
    parse_function=parse_prism_container,
)


def discovery_prism_container(section) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_prism_container(item: str, params, section) -> CheckResult:
    value_store = get_value_store()
    data = section.get(item)
    if not data:
        return

    capacity, freebytes = map(
        int,
        (
            data["usageStats"].get("storage.user_capacity_bytes", 0),
            data["usageStats"].get("storage.user_free_bytes", 0),
        ),
    )

    yield from df_check_filesystem_single(
        value_store=value_store,
        mountpoint=item,
        size_mb=capacity / 1024**2,
        avail_mb=freebytes / 1024**2,
        inodes_total=0,
        inodes_avail=0,
        reserved_mb=0,
        params=params,
    )


register.check_plugin(
    name="prism_containers",
    service_name="Container %s",
    sections=["prism_containers"],
    check_default_parameters=FILESYSTEM_DEFAULT_LEVELS,
    discovery_function=discovery_prism_container,
    check_function=check_prism_container,
    check_ruleset_name="filesystem",
)

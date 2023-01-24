#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
# ported by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
import ast
from typing import Any, Dict, Mapping

from .agent_based_api.v1 import register, render, Result, Service, State
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, StringTable

Section = Dict[str, Mapping[str, Any]]


def parse_pure_fa_drives(string_table: StringTable) -> Section:
    parsed: Section = {}
    data = ast.literal_eval(string_table[0][0])
    for element in data:
        parsed.setdefault(element.get("name", "unknown"), element)
    return parsed


register.agent_section(
    name="pure_fa_drives",
    parse_function=parse_pure_fa_drives,
)


def discovery_pure_fa_drives(section: Section) -> DiscoveryResult:
    for item in section:
        if section[item].get("status") == "unused":
            continue
        yield Service(item=item)


def check_pure_fa_drives(item: str, section: Section) -> CheckResult:
    data = section.get(item)
    if not data:
        return

    _DISK_STATES = {
        "empty": 0, 
        "failed": 2,
        "healthy": 0,
        "identifying": 1,
        "missing": 2,
        "recovering": 1,
        "unadmitted": 1,
        "unhealthy": 2,
        "unrecognized": 2,
        "updating": 1,
    }

    state = _DISK_STATES.get(data.get("status", ""), 3)
    message = "Protocol: %s, Type: %s, Capacity: %s, State: %s" % (data.get("protocol"), data.get("type"), render.bytes(data.get("capacity", 0)), data.get("status"))

    yield Result(state=State(state), summary=message)


register.check_plugin(
    name="pure_fa_drives",
    service_name="Pure Drive %s",
    sections=["pure_fa_drives"],
    discovery_function=discovery_pure_fa_drives,
    check_function=check_pure_fa_drives,
)

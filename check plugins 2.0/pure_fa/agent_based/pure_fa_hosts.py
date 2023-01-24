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


def parse_pure_fa_hosts(string_table: StringTable) -> Section:
    parsed: Section = {}
    data = ast.literal_eval(string_table[0][0])
    for element in data:
        parsed.setdefault(element.get("name", "unknown"), element)
    return parsed


register.agent_section(
    name="pure_fa_hosts",
    parse_function=parse_pure_fa_hosts,
)


def discovery_pure_fa_hosts(section: Section) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_pure_fa_hosts(item: str, section: Section) -> CheckResult:
    data = section.get(item)
    if not data:
        return

    message = "Hostgroup: %s, WWNs: %s" %( data.get("hgroup", "not defined"), ",".join(data.get("wwn", [])))

    yield Result(state=State.OK, summary=message)


register.check_plugin(
    name="pure_fa_hosts",
    service_name="Pure Host %s",
    sections=["pure_fa_hosts"],
    discovery_function=discovery_pure_fa_hosts,
    check_function=check_pure_fa_hosts,
)

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


def parse_pure_fa_hw(string_table: StringTable) -> Section:
    parsed: Section = {}
    data = ast.literal_eval(string_table[0][0])
    for element in data:
        parsed.setdefault(element.get("name", "unknown"), element)
    return parsed


register.agent_section(
    name="pure_fa_hw",
    parse_function=parse_pure_fa_hw,
)

def discovery_pure_fa_hw(section: Section) -> DiscoveryResult:
    if section:
        yield Service()


def check_pure_fa_hw(section: Section) -> CheckResult:
    if not section:
        return

    _HW_STATES = {
        "ok": 0,
        "not_installed": 0,
    }

    status = 0
    problem_list = []
    for element in section:
        element_state = _HW_STATES.get(section[element].get("status"), 2)
        if element_state != 0:
            problem_list.append(section[element].get("name"))
        status = max(status, element_state)

    message = "Overall state: %s" % status
    if len(problem_list) >= 1:
        message += "Problems: %s" % ",".join(problem_list)

    yield Result(state=State(status), summary=message)


register.check_plugin(
    name="pure_fa_hw",
    service_name="Pure Global Hardware State",
    sections=["pure_fa_hw"],
    discovery_function=discovery_pure_fa_hw,
    check_function=check_pure_fa_hw,
)


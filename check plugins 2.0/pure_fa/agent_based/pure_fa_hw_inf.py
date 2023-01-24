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


def discovery_pure_fa_hw_inf(section: Section) -> DiscoveryResult:
    for item in section:
        if not section[item].get("speed"):
            continue
        if section[item].get("speed") == 0:
            continue
        yield Service(item=item)


def check_pure_fa_hw_inf(item: str, section: Section) -> CheckResult:
    data = section.get(item)
    if not data:
        return

    _HW_STATES = {
        "ok": 0,
        "not_installed": 1,
    }

    status = _HW_STATES.get(data.get("status"), 3)

    message = "State : %s, Speed: %s" % (data.get("status", "unknown"), render.nicspeed(data.get("speed", 0)/8))

    yield Result(state=State(status), summary=message)


register.check_plugin(
    name="pure_fa_hw_inf",
    service_name="Pure Interface %s",
    sections=["pure_fa_hw"],
    discovery_function=discovery_pure_fa_hw_inf,
    check_function=check_pure_fa_hw_inf,
)

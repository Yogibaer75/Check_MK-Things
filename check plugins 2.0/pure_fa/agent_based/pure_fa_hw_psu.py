#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
# ported by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
import ast
from typing import Any, Dict, Mapping

from .agent_based_api.v1 import check_levels, register, Service, get_value_store 
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, StringTable
from .utils.temperature import check_temperature, TempParamDict

Section = Dict[str, Mapping[str, Any]]


def discovery_pure_fa_hw_psu(section: Section) -> DiscoveryResult:
    for item in section:
        if not section[item].get("voltage"):
            continue
        yield Service(item=item)


def check_pure_fa_hw_psu(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:
    data = section.get(item)
    if not data:
        return

    _HW_STATES = {
        "ok": 0,
        "not_installed": 1,
    }

    status = _HW_STATES.get(data.get("status"), 3)

    yield from check_levels(
        value = data.get("voltage", 0),
        metric_name="voltage",
        levels_upper=params['levels'],
        levels_lower=params['levels_lower'],
        render_func=lambda retval: '%.2f V' % retval,
        boundaries=(180,250),
    )


register.check_plugin(
    name="pure_fa_hw_psu",
    service_name="Pure PSU %s",
    sections=["pure_fa_hw"],
    discovery_function=discovery_pure_fa_hw_psu,
    check_function=check_pure_fa_hw_psu,
    check_default_parameters={'levels':(240,250),'levels_lower':(210,190)},
    check_ruleset_name="pure_psu",
)

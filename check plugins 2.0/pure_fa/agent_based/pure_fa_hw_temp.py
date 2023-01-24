#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
# ported by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
import ast
from typing import Any, Dict, Mapping

from .agent_based_api.v1 import register, Service, get_value_store 
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, StringTable
from .utils.temperature import check_temperature, TempParamDict

Section = Dict[str, Mapping[str, Any]]


def discovery_pure_fa_hw_temp(section: Section) -> DiscoveryResult:
    for item in section:
        if not section[item].get("temperature"):
            continue
        yield Service(item=item)


def check_pure_fa_hw_temp(item: str, params: TempParamDict, section: Section) -> CheckResult:
    data = section.get(item)
    if not data:
        return

    _HW_STATES = {
        "ok": 0,
        "not_installed": 1,
    }

    status = _HW_STATES.get(data.get("status"), 3)

    yield from check_temperature(
        data.get("temperature", 0),
        params,
        unique_name="pure_fa_%s" % item,
        value_store=get_value_store(),
        dev_status=status,
    )


register.check_plugin(
    name="pure_fa_hw_temp",
    service_name="Pure Temp %s",
    sections=["pure_fa_hw"],
    discovery_function=discovery_pure_fa_hw_temp,
    check_function=check_pure_fa_hw_temp,
    check_default_parameters={},
    check_ruleset_name="temperature",
)

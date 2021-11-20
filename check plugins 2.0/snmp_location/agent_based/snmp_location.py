#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from typing import (
    Mapping,
    Any,
)

from .agent_based_api.v1 import (
    exists,
    register,
    SNMPTree,
    type_defs,
    Service,
    Result,
    State,
)

Section = Mapping[str, Any]


def parse_snmp_location(string_table):
    return string_table if any(string_table) else None


register.snmp_section(
    name="snmp_location",
    parse_function=parse_snmp_location,
    fetch=[
        SNMPTree(
            base=".1.3.6.1.2.1.1",
            oids=[
                '6.0',  # sysLocation
            ],
        ),
    ],
    detect=exists(".1.3.6.1.2.1.1.1.0"),
)


def discover_snmp_location(section: Section) -> type_defs.DiscoveryResult:
    if section:
        yield Service()


def check_snmp_location(section: Section, ) -> type_defs.CheckResult:
    if len(section[0]) == 1:
        if section[0][0] == "unknown":
            numstate = 1
            infotxt = "Standort nicht gepflegt"
        else:
            numstate = 0
            infotxt = "Standort - " + ', '.join(section[0][0])
    else:
        numstate = 3
        infotxt = "No data received"
    yield Result(state=State(numstate), summary=infotxt)


register.check_plugin(
    name="snmp_location",
    service_name="Location",
    discovery_function=discover_snmp_location,
    check_function=check_snmp_location,
)

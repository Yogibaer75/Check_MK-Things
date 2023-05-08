#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# Example output
#<<<ilo_firmware:sep(124)>>>
#N/A|Embedded Storage Controller
#N/A|PCI-E Slot 2 Unknown
#8.32|Embedded Smart Array P420 Controller

from typing import NamedTuple, Sequence

from .agent_based_api.v1 import register, TableRow
from .agent_based_api.v1.type_defs import InventoryResult, StringTable


class FWEntry(NamedTuple):
    component: str
    version: str


Section = Sequence[FWEntry]


def parse_ilo_firmware(string_table: StringTable) -> Section:
    entries = []
    for line in string_table:
        if len(line) >= 2:
            entry = FWEntry(
                component=line[1],
                version=line[0],
            )
            entries.append(entry)
    return entries


register.agent_section(
    name="ilo_firmware",
    parse_function=parse_ilo_firmware,
)


def inventory_ilo_firmware(section: Section) -> InventoryResult:
    path = ["hardware", "firmware", "hpe"]
    for entry in section:
        yield TableRow(
            path=path,
            key_columns={
                "component": entry.component,
            },
            inventory_columns={
                "version": entry.version,
            },
            status_columns={},
        )


register.inventory_plugin(
    name="ilo_firmware",
    inventory_function=inventory_ilo_firmware,
)

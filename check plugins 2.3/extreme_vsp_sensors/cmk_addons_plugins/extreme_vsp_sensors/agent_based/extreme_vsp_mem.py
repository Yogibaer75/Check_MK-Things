#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Mapping, Optional

from cmk.agent_based.v2 import (
    SimpleSNMPSection,
    SNMPTree,
    StringTable,
    all_of,
    startswith,
)
from cmk.plugins.lib.netextreme import DETECT_NETEXTREME

Section = Mapping[str, float]

DETECT_VSP = all_of(
    startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1916.2.325"),
    startswith(".1.3.6.1.2.1.1.1.0", "VSP-74"),
)


def parse_extreme_vsp_mem(string_table: StringTable) -> Optional[Section]:
    """
    >>> parse_extreme_vsp_mem(([["1113454", "260459760"]]))
    {'MemFree': 260459760, 'MemTotal': 261573214}
    """
    if not string_table:
        return None
    total = int(string_table[0][1]) + int(string_table[0][0])
    return {
        "MemFree": int(string_table[0][1]) * 1024,
        "MemTotal": total * 1024,
    }


snmp_section_extreme_vsp_mem = SimpleSNMPSection(
    name="extreme_vsp_mem",
    parsed_section_name="mem_used",
    parse_function=parse_extreme_vsp_mem,
    detect=DETECT_NETEXTREME,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.2272.1.85.10.1.1",
        oids=[
            "6",  # memUsed
            "7",  # memFree
        ],
    ),
)

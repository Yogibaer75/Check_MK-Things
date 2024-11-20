#!/usr/bin/env python3
'''functions used by multiple parts of the plugin'''
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

import json
from typing import Dict
from cmk.agent_based.v2 import (
    DiscoveryResult,
    Service,
    StringTable,
)

HuaweiAPIData = Dict[str, object]
HuaweiHealthStatus = Dict[str, object]

huawei_running_state = {
    "0": ("unknown", 3),
    "1": ("normal", 0),
    "2": ("running", 0),
    "5": ("sleep in high temperature", 1),
    "10": ("link up", 0),
    "11": ("link down", 1),
    "12": ("powering on", 0),
    "13": ("powered off", 1),
    "14": ("pre-copy", 0),
    "16": ("reconstruction", 1),
    "27": ("online", 0),
    "28": ("offline", 1),
    "32": ("balancing", 0),
    "33": ("to be recovered", 1),
    "48": ("charging", 1),
    "49": ("carging completed", 0),
    "50": ("discharging", 0),
    "53": ("initializing", 1),
    "103": ("power-on failed", 2),
}

huawei_health_state = {
    "0": ("unknown", 3),
    "1": ("Normal", 0),
    "2": ("Fault", 2),
    "3": ("Pre-fail", 1),
    "4": ("Partially broken", 1),
    "5": ("Degraded", 1),
    "6": ("Bad sectors found", 1),
    "7": ("Bit errors found", 1),
    "8": ("Consistent", 0),
    "9": ("Inconsistent", 1),
    "10": ("Busy", 1),
    "11": ("No input", 1),
    "12": ("Low battery", 1),
    "13": ("Single link fault", 1),
    "14": ("Invalid", 2),
    "15": ("Write protect", 1),
}


def check_huawei_health(data: HuaweiAPIData) -> HuaweiHealthStatus:
    '''health state of on component'''
    state = {}
    if data.get("HEALTHSTATUS"):
        state.setdefault("Health state", huawei_health_state.get(data.get("HEALTHSTATUS", "0")))
    if data.get("RUNNINGSTATUS"):
        state.setdefault("Running state", huawei_running_state.get(data.get("RUNNINGSTATUS", "0")))
    return state


def parse_huawei_dorado(string_table: StringTable) -> HuaweiAPIData:
    '''parse data into dictionary'''
    parsed = {}

    for line in string_table:
        entry = {}
        try:
            entry = json.loads(line[0])
        except (IndexError, json.decoder.JSONDecodeError):
            continue
        if not entry.get('ID'):
            continue
        if entry.get('LOCATION') and entry.get('LOCATION') != "--":
            entry_id = entry.get('LOCATION')
        else:
            entry_id = entry.get('ID')
        parsed.setdefault(entry_id, entry)
    return parsed


def discover_huawei_dorado_items(section: HuaweiAPIData) -> DiscoveryResult:
    '''discover one item per key'''
    for key, data in section.items():
        if data.get("RUNNINGSTATUS") == "11":
            continue
        yield Service(item=key)

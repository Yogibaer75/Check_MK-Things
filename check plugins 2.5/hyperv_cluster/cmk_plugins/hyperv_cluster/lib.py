#!/usr/bin/python

import json
from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import (
    StringTable,
)

Section = Mapping[str, Mapping[str, str]]


def hyperv_vm_general(string_table: StringTable) -> Mapping[str, Mapping[str, str]]:
    parsed: dict[str, dict[str, str]] = {}
    single_host: dict[str, str] = {}
    foundit = False
    host_name: str = ""
    for line in string_table:
        if line[0] == "runtime.host":
            foundit = True
            host_name = line[1]
        if line[0] == "name" and foundit:
            foundit = False
            parsed[host_name] = single_host
            single_host = {}
            host_name = ""
        single_host[line[0]] = " ".join(line[1:])
    if foundit and single_host and host_name:
        parsed[host_name] = single_host
    return parsed


def hyperv_vm_convert(string_table: StringTable) -> Mapping[str, str]:
    parsed: dict[str, str] = {}
    for line in string_table:
        parsed[line[0]] = " ".join(line[1:])

    return parsed


COUNTER_TRANSLATIONS = {
    "durchschnittl. warteschlangenlänge der datenträger-lesevorgänge": "avg. disk read queue length",
    "durchschnittl. warteschlangenlänge der datenträger-schreibvorgänge": "avg. disk write queue length",
    "mittlere sek./lesevorgänge": "avg. disk sec/read",
    "mittlere sek./schreibvorgänge": "avg. disk sec/write",
    "lesevorgänge/s": "disk reads/sec",
    "schreibvorgänge/s": "disk writes/sec",
    "bytes gelesen/s": "disk read bytes/sec",
    "bytes geschrieben/s": "disk write bytes/sec",
}


def parse_hyperv_io(string_table: StringTable) -> Section:
    r"""Parse the CSV IO counters

    Lines read "<CSV name>\<counter> <value>". Older versions of the agent plug-in
    wrote "\\<node>\<CSV name>\<counter> <value>" with localized counter names.

    >>> parse_hyperv_io([["Volume1\\disk", "reads/sec", "12"]])
    {'Volume1': {'disk reads/sec': '12', 'node': ''}}
    >>> parse_hyperv_io([["\\\\hv01\\Volume1\\lesevorgänge/s", "12,5"]])
    {'Volume1': {'disk reads/sec': '12,5', 'node': 'hv01'}}
    """
    parsed: dict[str, dict[str, str]] = {}
    for line in string_table:
        value = line[-1]
        match " ".join(line[:-1]).split("\\", 4):
            case [lun, name]:
                host = ""
            case ["", "", host, lun, name]:
                pass
            case _:
                continue
        lun_data = parsed.setdefault(lun, {})
        lun_data[COUNTER_TRANSLATIONS.get(name, name)] = value
        lun_data["node"] = host
    return parsed


def merge_node_sections(section: Mapping[str, Section | None]) -> Section:
    """Combine the reports of the nodes of a Checkmk cluster host

    Every node of the failover cluster reports the same cluster-wide data. For each
    item, use the report of the first node, in the order of the node names.

    >>> merge_node_sections(
    ...     {"HV02": {"A": {"x": "2"}, "B": {}}, "HV01": {"A": {"x": "1"}}, "HV03": None}
    ... )
    {'A': {'x': '1'}, 'B': {}}
    """
    merged: dict[str, Mapping[str, str]] = {}
    for node in sorted(section):
        for item, data in (section[node] or {}).items():
            merged.setdefault(item, data)
    return merged


def parse_hyperv(string_table: StringTable) -> dict[str, dict[str, Any]]:
    datatypes = {
        "vhd": "vhd.name",
        "nic": "nic.name",
        "checkpoints": "checkpoint.name",
        "cluster.number_of_nodes": "cluster.node.name",
        "cluster.number_of_csv": "cluster.csv.name",
        "cluster.number_of_disks": "cluster.disk.name",
        "cluster.number_of_vms": "cluster.vm.name",
        "cluster.number_of_networks": "cluster.network.name",
    }

    parsed: dict[str, dict[str, Any]] = {}
    if len(string_table) == 0:
        return parsed

    datatype = datatypes.get(string_table[0][0])
    element = ""
    start = False
    _count = int(string_table[0][1])
    counter = 1
    for line in string_table:
        if line[0].lower() == datatype:
            if start:
                counter += 1
            else:
                start = True
            if datatype == "nic.name":
                element = " ".join(line[1:]) + f" {counter}"
            else:
                element = " ".join(line[1:])
            parsed[element] = {}
        elif start:
            parsed[element][str(line[0])] = " ".join(line[1:])

    return parsed


def parse_hyperv_json_multi(string_table: StringTable) -> dict[str, dict[str, Any | bool| str]]:
    dict_keys = ["vhd.Name", "nic.id", "checkpoint.name", "name"]
    parsed: dict[str, dict[str, Any | bool| str]] = {}
    for line in string_table:
        try:
            data = json.loads(line[0])
        except json.JSONDecodeError:
            continue
        key = next((x for x in dict_keys if x in data), None)
        if key:
            parsed[data[key]] = data

    return parsed


def parse_hyperv_json(string_table: StringTable) -> dict[str, Any | bool| str]:
    parsed: dict[str, Any | bool| str] = {}
    for line in string_table:
        try:
            data = json.loads(line[0])
        except json.JSONDecodeError:
            continue
        parsed.update(data)

    return parsed

#!/usr/bin/python

from collections.abc import Mapping

from cmk.agent_based.v2 import (  # type: ignore[import]
    StringTable,
)

Section = Mapping[str, Mapping[str, str]]

def hyperv_vm_general(string_table):
    parsed = {}
    single_host = {}
    foundit = False
    host_name = ""
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


def hyperv_vm_convert(string_table):
    parsed = {}
    for line in string_table:
        parsed[line[0]] = " ".join(line[1:])

    return parsed


counter_translation = {
    "durchschnittl. warteschlangenlänge der datenträger-lesevorgänge": "avg. disk read queue length", # NOQA: E501
    "durchschnittl. warteschlangenlänge der datenträger-schreibvorgänge": "avg. disk write queue length", # NOQA: E501
    "mittlere sek./lesevorgänge": "avg. disk sec/read",
    "mittlere sek./schreibvorgänge": "avg. disk sec/write",
    "lesevorgänge/s": "disk reads/sec",
    "schreibvorgänge/s": "disk writes/sec",
    "bytes gelesen/s": "disk read bytes/sec",
    "bytes geschrieben/s": "disk write bytes/sec",
}

HYPERV_IO_SPLIT_SIMPLE = 2
HYPERV_IO_SPLIT_EXTENDED = 5


def parse_hyperv_io(string_table: StringTable) -> Section:
    parsed: dict[str, dict[str, str]] = {}
    for line in string_table:
        value = line[-1]
        data = " ".join(line[:-1])
        splitted_data = data.split("\\", 4)
        if len(splitted_data) == HYPERV_IO_SPLIT_SIMPLE:
            lun, name = splitted_data
            host = ""
        elif len(splitted_data) == HYPERV_IO_SPLIT_EXTENDED:
            _empty, _empty2, host, lun, name = splitted_data
        else:
            continue
        if name in counter_translation.keys():
            name = counter_translation[name]
        if lun not in parsed:
            parsed[lun] = {}
        parsed[lun][name] = value
        parsed[lun]["node"] = host
    return parsed


def parse_hyperv(string_table):
    datatypes = {
        "vhd": "vhd.name",
        "nic": "nic.name",
        "checkpoints": "checkpoint.name",
        "cluster.number_of_nodes": "cluster.node.name",
        "cluster.number_of_csv": "cluster.csv.name",
        "cluster.number_of_disks": "cluster.disk.name",
        "cluster.number_of_vms": "cluster.vm.name",
        "cluster.number_of_roles": "cluster.role.name",
        "cluster.number_of_networks": "cluster.network.name",
    }

    parsed = {}
    if len(string_table) == 0:
        return parsed

    datatype = datatypes.get(string_table[0][0])
    datatype_name = string_table[0][0]
    element = ""
    start = False
    _count = int(string_table[0][1])
    counter = 1
    for line in string_table:
        if line[0].lower() == datatype:
            if start is True:
                counter += 1
            else:
                start = True
            if datatype == "nic.name":
                element = " ".join(line[1:]) + f" {counter}"
            else:
                element = " ".join(line[1:])
            parsed[element] = {}
        elif start:
            parsed[element][line[0]] = " ".join(line[1:])

    if datatype_name == "checkpoints" and parsed == {}:
        return {"no_checkpoints": True}
    return parsed


def parse_hyperv_nic(string_table):
    parsed = {}
    if len(string_table) == 0:
        return parsed

    _number_of_nics = int(string_table[0][1])
    counter = 1
    start = False
    nic_id = ""
    data = {}
    for line in string_table:
        if line[0] == "nic.name" and start:
            start = False
            if nic_id not in parsed.keys():
                parsed[nic_id] = data
            nic_id = ""
            data = {}
        if line[0] == "nic.id" and not start:
            start = True
            nic_id = line[1]
        if line[0] == "nic.name":
            data[line[0]] = f"{' '.join(line[1:])} {counter}"
            counter += 1
        else:
            data[line[0]] = " ".join(line[1:])
    if start and data and nic_id:
        if nic_id not in parsed.keys():
            parsed[nic_id] = data
    return parsed

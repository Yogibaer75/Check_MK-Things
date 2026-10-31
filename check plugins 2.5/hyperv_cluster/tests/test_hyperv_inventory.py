#!/usr/bin/env python3
# Unit tests for the Hyper-V HW/SW inventory (cmk.plugins.hyperv_cluster.agent_based.hyperv_inventory)
# Run inside the site: pytest ~/local/lib/python3/cmk/plugins/tests/hyperv_cluster
# Data snippets are reduced copies of real hyperv_host.ps1 / hyperv_cluster.ps1 output.

from cmk.agent_based.v2 import Attributes, TableRow
from cmk.plugins.hyperv_cluster.agent_based import hyperv_inventory as inv
from cmk.plugins.hyperv_cluster.agent_based.hyperv_vm_nic import parse_hyperv_vm_nic_json
from cmk.plugins.hyperv_cluster.agent_based.hyperv_vm_ram import parse_hyperv_vm_ram_json
from cmk.plugins.hyperv_cluster.agent_based.hyperv_vm_vhd import parse_hyperv_vm_vhd_json
from cmk.plugins.hyperv_cluster.lib import hyperv_vm_convert, parse_hyperv, parse_hyperv_json

GENERAL = [
    ['{"name":"SQL01","cluster.clustered":true,"runtime.host":"HV01","runtime.powerState":"Running",'
     '"config.vmid":"50ccfcde","config.generation":2,"config.version":"10.0",'
     '"config.creationTime":"2020-12-20T13:01:31.6753440+01:00","replication.mode":"None",'
     '"runtime.Notes":"","config.AutomaticStartDelay":0,"security.TPMEnabled":false,'
     '"guest.os":"Windows Server 2019 Datacenter"}']
]
CPU = [['{"config.hardware.numCPU":8,"config.hardware.NestedVirtualization":false}']]
RAM = [
    ['{"config.hardware.StartRAM":85899345920,"config.hardware.MinRAM":536870912,'
     '"config.hardware.MaxRAM":1099511627776,"config.hardware.RAMType":false,'
     '"config.hardware.AssignedRAM":85899345920,"config.hardware.RAMDemand":77309411328}']
]
NIC = [
    ['{"nic.security.RouterGuard":1,"nic.security.DHCPGuard":0,"nic.dynamicMAC":true,'
     '"nic.MAC":"00155D1F7B64","nic.IPAddresses":["172.20.11.132","fe80::1"],"nic.vswitch":"vSwitch1",'
     '"nic.connectionstate":true,"nic.id":"Microsoft:50CC\\\\26A71897","nic.name":"Netzwerkkarte",'
     '"nic.VLAN.mode":"Access","nic.VLAN.id":11}']
]
VHD = [
    ['{"vhd.Name":"Festplatte","vhd.Path":"C:\\\\VM\\\\SQL01.VHDX","vhd.controller.Type":1,'
     '"vhd.controller.Location":2,"vhd.controller.Number":0,"vhd.Type":"Dynamic",'
     '"vhd.DiskSize":1099511627776,"vhd.FileSize":413394796544}']
]


def test_inventory_vm() -> None:
    (result,) = inv.inventory_hyperv_vm(
        parse_hyperv_json(GENERAL), parse_hyperv_json(CPU), parse_hyperv_vm_ram_json(RAM)
    )
    assert isinstance(result, Attributes)
    attrs = result.inventory_attributes
    assert attrs["name"] == "SQL01" and attrs["generation"] == 2 and attrs["vcpus"] == 8
    assert attrs["created"] == 1608465691
    assert attrs["replication_mode"] is None and attrs["notes"] is None
    assert attrs["automatic_start_delay"] == 0 and attrs["tpm"] is False
    assert attrs["dynamic_memory"] is False and attrs["max_ram"] is None
    assert result.status_attributes["assigned_ram"] == 85899345920


def test_inventory_vm_nic() -> None:
    (row,) = inv.inventory_hyperv_vm_nic(parse_hyperv_vm_nic_json(NIC))
    assert isinstance(row, TableRow)
    assert row.key_columns == {"id": "26A71897"}
    assert row.inventory_columns["macaddress"] == "00:15:5D:1F:7B:64"
    assert row.inventory_columns["vlan_id"] == 11
    assert row.inventory_columns["dhcp_guard"] is True
    assert row.inventory_columns["router_guard"] is False
    assert row.status_columns["ipv4_address"] == "172.20.11.132"
    assert row.status_columns["ipv6_address"] == "fe80::1"


def test_inventory_vm_vhd() -> None:
    (row,) = inv.inventory_hyperv_vm_vhd(parse_hyperv_vm_vhd_json(VHD))
    assert isinstance(row, TableRow)
    assert row.key_columns == {"controller": "1 0 2"}
    assert row.inventory_columns["bus"] == "SCSI"
    assert row.inventory_columns["size"] == 1099511627776
    assert row.status_columns["file_size"] == 413394796544


def test_inventory_cluster() -> None:
    general = hyperv_vm_convert([["cluster.name", "HVCLU"], ["quorum.type", "Majority"]])
    nodes = parse_hyperv(
        [
            ["cluster.number_of_nodes", "1"],
            ["cluster.node.name", "HV02"],
            ["cluster.node.id", "1"],
            ["cluster.node.state", "Up"],
            ["cluster.node.info"],
            ["cluster.node_vendor.manufacturer", "Dell", "Inc."],
            ["cluster.node_vendor.serial", "ABCD1234"],
        ]
    )
    result = list(inv.inventory_hyperv_cluster(general, nodes, None, None, None, None))
    assert result[0] == Attributes(
        path=["software", "applications", "hyperv", "cluster"],
        inventory_attributes={
            "name": "HVCLU",
            "ip": None,
            "subnet": None,
            "quorum_type": "Majority",
            "quorum_resource": None,
            "nodes": 1,
        },
    )
    assert isinstance(row := result[1], TableRow)
    assert row.key_columns == {"name": "HV02"}
    assert row.inventory_columns["manufacturer"] == "Dell Inc."
    assert row.status_columns == {"state": "Up", "status_information": None}

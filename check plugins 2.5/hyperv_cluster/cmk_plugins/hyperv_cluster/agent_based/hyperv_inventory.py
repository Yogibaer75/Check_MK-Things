#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
"""HW/SW inventory of Hyper-V clusters, nodes and VMs

All data is placed below software.applications.hyperv. The VM data is reported as
piggyback data, often to the same host that also runs a Checkmk agent inside the
guest. Writing to hardware.* or software.os would mix the hypervisor's view with
the guest's own inventory.
"""

import ast
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    Attributes,
    InventoryPlugin,
    InventoryResult,
    TableRow,
)
from cmk.plugins.hyperv_cluster.agent_based.hyperv_vm_ram import Section as RamSection
from cmk.plugins.hyperv_cluster.agent_based.hyperv_vm_vhd import Section as VhdSection
from cmk.plugins.hyperv_cluster.lib import Section, parse_hyperv_json

_PATH = ["software", "applications", "hyperv"]

# Microsoft.HyperV.PowerShell.ControllerType
_CONTROLLER_TYPES = {"0": "IDE", "1": "SCSI", "2": "PMEM"}


def _value(value: Any) -> Any:
    """Normalize values of the JSON sections and of the stringified legacy sections"""
    if value is None or value in ("", "None", "null"):
        return None
    if isinstance(value, str) and value.lower() in ("true", "false"):
        return value.lower() == "true"
    return value


def _int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _on_off(value: Any) -> bool | None:
    """Microsoft.HyperV.PowerShell.OnOffState: On = 0, Off = 1"""
    match _value(value):
        case 0 | "0" | "On":
            return True
        case 1 | "1" | "Off":
            return False
    return None


def _timestamp(value: Any) -> int | None:
    """Older agents sent a Unix timestamp, newer ones an ISO 8601 string"""
    if (timestamp := _int(value)) is not None:
        return timestamp
    try:
        return int(datetime.fromisoformat(str(value)).timestamp())
    except ValueError:
        return None


def _mac(value: Any) -> str | None:
    if not (mac := _value(value)):
        return None
    mac = str(mac).replace("-", "").replace(":", "").upper()
    return ":".join(mac[i : i + 2] for i in range(0, len(mac), 2))


def _ip_addresses(value: Any) -> tuple[str | None, str | None]:
    """The NIC parser stringifies the address list, e.g. "['10.0.0.1', 'fe80::1']" """
    if isinstance(value, str):
        try:
            value = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            value = value.split()
    addresses = [str(a) for a in value] if isinstance(value, list | tuple) else []
    ipv4 = ", ".join(a for a in addresses if ":" not in a)
    ipv6 = ", ".join(a for a in addresses if ":" in a)
    return ipv4 or None, ipv6 or None


def inventory_hyperv_cluster(
    section_hyperv_cluster_general: Mapping[str, str] | None,
    section_hyperv_cluster_nodes: Section | None,
    section_hyperv_cluster_network: Section | None,
    section_hyperv_cluster_disks: Section | None,
    section_hyperv_cluster_csv: Section | None,
    section_hyperv_cluster_roles: Section | None,
) -> InventoryResult:
    path = [*_PATH, "cluster"]
    if general := section_hyperv_cluster_general:
        yield Attributes(
            path=path,
            inventory_attributes={
                "name": _value(general.get("cluster.name")),
                "ip": _value(general.get("cluster.ip")),
                "subnet": _value(general.get("cluster.subnet")),
                "quorum_type": _value(general.get("quorum.type")),
                "quorum_resource": _value(general.get("quorum.resourcename")),
                "nodes": len(section_hyperv_cluster_nodes or {}) or None,
            },
        )

    for name, node in (section_hyperv_cluster_nodes or {}).items():
        yield TableRow(
            path=[*path, "nodes"],
            key_columns={"name": name},
            inventory_columns={
                "id": _int(node.get("cluster.node.id")),
                "weight": _int(node.get("cluster.node.weight")),
                "manufacturer": _value(node.get("cluster.node_vendor.manufacturer")),
                "model": _value(node.get("cluster.node_vendor.model")),
                "serial": _value(node.get("cluster.node_vendor.serial")),
            },
            status_columns={
                "state": _value(node.get("cluster.node.state")),
                "status_information": _value(node.get("cluster.node.info")),
            },
        )

    for name, network in (section_hyperv_cluster_network or {}).items():
        yield TableRow(
            path=[*path, "networks"],
            key_columns={"name": name},
            inventory_columns={
                "role": _value(network.get("cluster.network.role")),
                "ipv4_address": _value(
                    network.get("cluster.network.ipv4_address") or network.get("cluster.network.ip")
                ),
                "netmask": _value(network.get("cluster.network.netmask")),
                "ipv6_address": _value(network.get("cluster.network.ipv6_address")),
            },
            status_columns={"state": _value(network.get("cluster.network.state"))},
        )

    for name, disk in (section_hyperv_cluster_disks or {}).items():
        yield TableRow(
            path=[*path, "disks"],
            key_columns={"name": name},
            inventory_columns={"owner_group": _value(disk.get("cluster.disk.owner_group"))},
            status_columns={
                "owner_node": _value(disk.get("cluster.disk.owner_node")),
                "state": _value(disk.get("cluster.disk.state")),
            },
        )

    for name, csv in (section_hyperv_cluster_csv or {}).items():
        yield TableRow(
            path=[*path, "csv"],
            key_columns={"name": name},
            inventory_columns={
                "volume": _value(csv.get("cluster.csv.volume")),
                "size": _int(csv.get("cluster.csv.size")),
            },
            status_columns={
                "owner": _value(csv.get("cluster.csv.owner")),
                "free_space": _int(csv.get("cluster.csv.free_space")),
            },
        )

    for name, vm in (section_hyperv_cluster_roles or {}).items():
        yield TableRow(
            path=[*path, "vms"],
            key_columns={"name": name},
            status_columns={
                "state": _value(vm.get("cluster.vm.state")),
                "owner": _value(vm.get("cluster.vm.owner")),
            },
        )


inventory_plugin_hyperv_cluster = InventoryPlugin(
    name="hyperv_cluster",
    sections=[
        "hyperv_cluster_general",
        "hyperv_cluster_nodes",
        "hyperv_cluster_network",
        "hyperv_cluster_disks",
        "hyperv_cluster_csv",
        "hyperv_cluster_roles",
    ],
    inventory_function=inventory_hyperv_cluster,
)


def inventory_hyperv_node(section: Mapping[str, Any]) -> InventoryResult:
    yield Attributes(
        path=[*_PATH, "host"],
        inventory_attributes={"name": _value(section.get("host"))},
        status_attributes={"vm_count": _int(section.get("vmCount"))},
    )


inventory_plugin_hyperv_node = InventoryPlugin(
    name="hyperv_node",
    inventory_function=inventory_hyperv_node,
)


# The agent plug-in has always sent this section, but no check uses it
agent_section_hyperv_vm_cpu_json = AgentSection(
    name="hyperv_vm_cpu_json",
    parse_function=parse_hyperv_json,
    parsed_section_name="hyperv_vm_cpu",
)


def inventory_hyperv_vm(
    section_hyperv_vm_general: Mapping[str, Any] | None,
    section_hyperv_vm_cpu: Mapping[str, Any] | None,
    section_hyperv_vm_ram: RamSection | None,
) -> InventoryResult:
    general = section_hyperv_vm_general or {}
    cpu = section_hyperv_vm_cpu or {}
    ram = section_hyperv_vm_ram
    if not (general or cpu or ram):
        return

    attributes: dict[str, Any] = {
        "name": general.get("name"),
        "vmid": general.get("config.vmid"),
        "generation": _int(general.get("config.generation")),
        "version": general.get("config.version"),
        "created": _timestamp(general.get("config.creationTime")),
        "clustered": general.get("cluster.clustered"),
        "path": general.get("config.Path"),
        "checkpoint_location": general.get("config.SnapshotFileLocation"),
        "checkpoint_type": general.get("config.CheckPointType"),
        "automatic_start_action": general.get("config.AutomaticStartAction"),
        "automatic_start_delay": _int(general.get("config.AutomaticStartDelay")),
        "automatic_stop_action": general.get("config.AutomaticStopAction"),
        "automatic_critical_error_action": general.get("config.AutomaticCriticalErrorAction"),
        "shielded": general.get("security.shieldedVM"),
        "tpm": general.get("security.TPMEnabled"),
        "state_migration_encrypted": general.get("security.StateMigrationEncrypted"),
        "replication_mode": general.get("replication.mode"),
        "replica_server": general.get("replication.CurrentServer"),
        "replication_frequency": _int(general.get("replication.frequency")),
        "notes": general.get("runtime.Notes"),
        "guest_fqdn": general.get("guest.fqdn"),
        "guest_os": general.get("guest.os"),
        "integration_services_version": general.get("guest.IntegrationServicesVersion"),
        "vcpus": _int(cpu.get("config.hardware.numCPU")),
        "nested_virtualization": cpu.get("config.hardware.NestedVirtualization"),
        "cpu_compatibility_migration": cpu.get("config.hardware.CompatibilityForMigration"),
        "cpu_compatibility_older_os": cpu.get("config.hardware.CompatibilityForOlderOS"),
        "host_resource_protection": cpu.get("config.hardware.HostResourceProtection"),
    }
    status_attributes: dict[str, Any] = {
        "power_state": general.get("runtime.powerState"),
        "host": general.get("runtime.host"),
        "replication_state": general.get("replication.state"),
        "replication_health": general.get("replication.health"),
    }
    if ram:
        attributes |= {
            "dynamic_memory": ram.is_dynamic,
            "startup_ram": ram.start_ram or None,
            "min_ram": ram.min_ram if ram.is_dynamic else None,
            "max_ram": ram.max_ram if ram.is_dynamic else None,
        }
        status_attributes["assigned_ram"] = ram.assigned_ram

    yield Attributes(
        path=[*_PATH, "vm"],
        inventory_attributes={k: _value(v) for k, v in attributes.items()},
        status_attributes={k: _value(v) for k, v in status_attributes.items()},
    )


inventory_plugin_hyperv_vm = InventoryPlugin(
    name="hyperv_vm",
    sections=["hyperv_vm_general", "hyperv_vm_cpu", "hyperv_vm_ram"],
    inventory_function=inventory_hyperv_vm,
)


def inventory_hyperv_vm_vhd(section: VhdSection) -> InventoryResult:
    for item, vhd in section.items():
        controller_type, number, location = (item.split() + ["", "", ""])[:3]
        yield TableRow(
            path=[*_PATH, "vm", "disks"],
            # Same as the item of the service "Hyper-V VM Disk"
            key_columns={"controller": item},
            inventory_columns={
                "bus": _CONTROLLER_TYPES.get(controller_type, controller_type or None),
                "controller_number": _int(number),
                "location": _int(location),
                "path": str(vhd.main_path),
                "type": str(vhd.type),
                "size": vhd.disk_size,
            },
            status_columns={"file_size": vhd.file_size},
        )


inventory_plugin_hyperv_vm_vhd = InventoryPlugin(
    name="hyperv_vm_vhd",
    inventory_function=inventory_hyperv_vm_vhd,
)


def inventory_hyperv_vm_nic(section: Mapping[str, Mapping[str, str]]) -> InventoryResult:
    for nic_id, nic in section.items():
        ipv4, ipv6 = _ip_addresses(nic.get("nic.IPAddresses"))
        yield TableRow(
            path=[*_PATH, "vm", "nics"],
            # Same as the item of the service "Hyper-V VM NIC"
            key_columns={"id": nic_id},
            inventory_columns={
                "name": _value(nic.get("nic.name")),
                "macaddress": _mac(nic.get("nic.MAC")),
                "dynamic_mac": _value(nic.get("nic.dynamicMAC")),
                "vswitch": _value(nic.get("nic.vswitch")),
                "vlan_mode": _value(nic.get("nic.VLAN.mode")),
                "vlan_id": _int(nic.get("nic.VLAN.id")),
                "dhcp_guard": _on_off(nic.get("nic.security.DHCPGuard")),
                "router_guard": _on_off(nic.get("nic.security.RouterGuard")),
            },
            status_columns={
                "connected": _value(nic.get("nic.connectionstate")),
                "ipv4_address": ipv4,
                "ipv6_address": ipv6,
            },
        )


inventory_plugin_hyperv_vm_nic = InventoryPlugin(
    name="hyperv_vm_nic",
    inventory_function=inventory_hyperv_vm_nic,
)


def inventory_hyperv_vm_integration(section: Mapping[str, Mapping[str, Any]]) -> InventoryResult:
    for name, service in section.items():
        yield TableRow(
            path=[*_PATH, "vm", "integration_services"],
            key_columns={"name": name},
            inventory_columns={"enabled": _value(service.get("enabled"))},
            status_columns={"status": _value(service.get("PrimaryStatusDescription"))},
        )


inventory_plugin_hyperv_vm_integration = InventoryPlugin(
    name="hyperv_vm_integration",
    sections=["hyperv_vm_integration_json"],
    inventory_function=inventory_hyperv_vm_integration,
)

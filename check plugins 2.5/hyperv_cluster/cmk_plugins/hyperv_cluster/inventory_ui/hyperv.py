#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

import time

from cmk.inventory_ui.v1_unstable import (
    AgeNotation,
    BoolField,
    DecimalNotation,
    IECNotation,
    Label,
    Node,
    NumberField,
    StrictPrecision,
    Table,
    TextField,
    Title,
    Unit,
    View,
)

UNIT_AGE = Unit(AgeNotation())
UNIT_BYTES = Unit(IECNotation("B"))
UNIT_COUNT = Unit(DecimalNotation(""), StrictPrecision(0))


def _render_date(value: int | float) -> Label | str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(value))


node_software_applications_hyperv = Node(
    name="software_applications_hyperv",
    path=["software", "applications", "hyperv"],
    title=Title("Hyper-V"),
)

node_software_applications_hyperv_host = Node(
    name="software_applications_hyperv_host",
    path=["software", "applications", "hyperv", "host"],
    title=Title("Host"),
    attributes={
        "name": TextField(Title("Name")),
        "vm_count": NumberField(Title("#VMs"), render=UNIT_COUNT),
    },
)

node_software_applications_hyperv_cluster = Node(
    name="software_applications_hyperv_cluster",
    path=["software", "applications", "hyperv", "cluster"],
    title=Title("Failover cluster"),
    attributes={
        "name": TextField(Title("Name")),
        "ip": TextField(Title("IP address")),
        "subnet": TextField(Title("Subnet mask")),
        "quorum_type": TextField(Title("Quorum type")),
        "quorum_resource": TextField(Title("Quorum resource")),
        "nodes": NumberField(Title("#Nodes"), render=UNIT_COUNT),
    },
)

node_software_applications_hyperv_cluster_nodes = Node(
    name="software_applications_hyperv_cluster_nodes",
    path=["software", "applications", "hyperv", "cluster", "nodes"],
    title=Title("Nodes"),
    table=Table(
        view=View(name="invhypervclusternodes", title=Title("Hyper-V cluster nodes")),
        columns={
            "name": TextField(Title("Name")),
            "id": NumberField(Title("ID"), render=UNIT_COUNT),
            "state": TextField(Title("State")),
            "status_information": TextField(Title("Status information")),
            "weight": NumberField(Title("Vote weight"), render=UNIT_COUNT),
            "manufacturer": TextField(Title("Manufacturer")),
            "model": TextField(Title("Model")),
            "serial": TextField(Title("Serial number")),
        },
    ),
)

node_software_applications_hyperv_cluster_networks = Node(
    name="software_applications_hyperv_cluster_networks",
    path=["software", "applications", "hyperv", "cluster", "networks"],
    title=Title("Networks"),
    table=Table(
        columns={
            "name": TextField(Title("Name")),
            "role": TextField(Title("Role")),
            "state": TextField(Title("State")),
            "ipv4_address": TextField(Title("IPv4 network")),
            "netmask": TextField(Title("Netmask")),
            "ipv6_address": TextField(Title("IPv6 network")),
        },
    ),
)

node_software_applications_hyperv_cluster_disks = Node(
    name="software_applications_hyperv_cluster_disks",
    path=["software", "applications", "hyperv", "cluster", "disks"],
    title=Title("Disks"),
    table=Table(
        columns={
            "name": TextField(Title("Name")),
            "owner_group": TextField(Title("Owner group")),
            "owner_node": TextField(Title("Owner node")),
            "state": TextField(Title("State")),
        },
    ),
)

node_software_applications_hyperv_cluster_csv = Node(
    name="software_applications_hyperv_cluster_csv",
    path=["software", "applications", "hyperv", "cluster", "csv"],
    title=Title("Cluster shared volumes"),
    table=Table(
        columns={
            "name": TextField(Title("Name")),
            "volume": TextField(Title("Volume")),
            "owner": TextField(Title("Owner node")),
            "size": NumberField(Title("Size"), render=UNIT_BYTES),
            "free_space": NumberField(Title("Free space"), render=UNIT_BYTES),
        },
    ),
)

node_software_applications_hyperv_cluster_vms = Node(
    name="software_applications_hyperv_cluster_vms",
    path=["software", "applications", "hyperv", "cluster", "vms"],
    title=Title("Clustered VMs"),
    table=Table(
        view=View(name="invhypervclustervms", title=Title("Hyper-V clustered VMs")),
        columns={
            "name": TextField(Title("Name")),
            "state": TextField(Title("State")),
            "owner": TextField(Title("Owner node")),
        },
    ),
)

node_software_applications_hyperv_vm = Node(
    name="software_applications_hyperv_vm",
    path=["software", "applications", "hyperv", "vm"],
    title=Title("Virtual machine"),
    attributes={
        "name": TextField(Title("Name")),
        "vmid": TextField(Title("VM ID")),
        "power_state": TextField(Title("Power state")),
        "host": TextField(Title("Running on host")),
        "generation": NumberField(Title("Generation"), render=UNIT_COUNT),
        "version": TextField(Title("Configuration version")),
        "created": NumberField(Title("Created"), render=_render_date),
        "clustered": BoolField(Title("Clustered")),
        "vcpus": NumberField(Title("#Virtual processors"), render=UNIT_COUNT),
        "dynamic_memory": BoolField(Title("Dynamic memory")),
        "startup_ram": NumberField(Title("Startup RAM"), render=UNIT_BYTES),
        "min_ram": NumberField(Title("Minimum RAM"), render=UNIT_BYTES),
        "max_ram": NumberField(Title("Maximum RAM"), render=UNIT_BYTES),
        "assigned_ram": NumberField(Title("Assigned RAM"), render=UNIT_BYTES),
        "guest_os": TextField(Title("Guest OS")),
        "guest_fqdn": TextField(Title("Guest FQDN")),
        "integration_services_version": TextField(Title("Integration services version")),
        "path": TextField(Title("Path")),
        "checkpoint_location": TextField(Title("Checkpoint location")),
        "checkpoint_type": TextField(Title("Checkpoint type")),
        "automatic_start_action": TextField(Title("Automatic start action")),
        "automatic_start_delay": NumberField(Title("Automatic start delay"), render=UNIT_AGE),
        "automatic_stop_action": TextField(Title("Automatic stop action")),
        "automatic_critical_error_action": TextField(Title("Automatic critical error action")),
        "shielded": BoolField(Title("Shielded VM")),
        "tpm": BoolField(Title("Virtual TPM")),
        "state_migration_encrypted": BoolField(Title("Encrypted state and migration traffic")),
        "nested_virtualization": BoolField(Title("Nested virtualization")),
        "cpu_compatibility_migration": BoolField(Title("Processor compatibility for migration")),
        "cpu_compatibility_older_os": BoolField(Title("Processor compatibility for older OS")),
        "host_resource_protection": BoolField(Title("Host resource protection")),
        "replication_mode": TextField(Title("Replication mode")),
        "replication_state": TextField(Title("Replication state")),
        "replication_health": TextField(Title("Replication health")),
        "replica_server": TextField(Title("Replica server")),
        "replication_frequency": NumberField(Title("Replication frequency"), render=UNIT_AGE),
        "notes": TextField(Title("Notes")),
    },
)

node_software_applications_hyperv_vm_disks = Node(
    name="software_applications_hyperv_vm_disks",
    path=["software", "applications", "hyperv", "vm", "disks"],
    title=Title("Virtual hard disks"),
    table=Table(
        view=View(name="invhypervvmdisks", title=Title("Hyper-V virtual hard disks")),
        columns={
            "controller": TextField(Title("Controller")),
            "bus": TextField(Title("Bus")),
            "controller_number": NumberField(Title("Controller number"), render=UNIT_COUNT),
            "location": NumberField(Title("Location"), render=UNIT_COUNT),
            "type": TextField(Title("Type")),
            "size": NumberField(Title("Capacity"), render=UNIT_BYTES),
            "file_size": NumberField(Title("File size"), render=UNIT_BYTES),
            "path": TextField(Title("Path")),
        },
    ),
)

node_software_applications_hyperv_vm_nics = Node(
    name="software_applications_hyperv_vm_nics",
    path=["software", "applications", "hyperv", "vm", "nics"],
    title=Title("Network adapters"),
    table=Table(
        view=View(name="invhypervvmnics", title=Title("Hyper-V VM network adapters")),
        columns={
            "id": TextField(Title("ID")),
            "name": TextField(Title("Name")),
            "macaddress": TextField(Title("MAC address")),
            "dynamic_mac": BoolField(Title("Dynamic MAC")),
            "ipv4_address": TextField(Title("IPv4 addresses")),
            "ipv6_address": TextField(Title("IPv6 addresses")),
            "vswitch": TextField(Title("Virtual switch")),
            "vlan_mode": TextField(Title("VLAN mode")),
            "vlan_id": NumberField(Title("VLAN ID"), render=UNIT_COUNT),
            "connected": BoolField(Title("Connected")),
            "dhcp_guard": BoolField(Title("DHCP guard")),
            "router_guard": BoolField(Title("Router guard")),
        },
    ),
)

node_software_applications_hyperv_vm_integration_services = Node(
    name="software_applications_hyperv_vm_integration_services",
    path=["software", "applications", "hyperv", "vm", "integration_services"],
    title=Title("Integration services"),
    table=Table(
        columns={
            "name": TextField(Title("Name")),
            "enabled": BoolField(Title("Enabled")),
            "status": TextField(Title("Status")),
        },
    ),
)

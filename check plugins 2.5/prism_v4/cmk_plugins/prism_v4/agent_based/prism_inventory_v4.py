#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
"""HW/SW inventory of Nutanix clusters, nodes and VMs (API v4)"""

from collections.abc import Mapping, Sequence
from typing import Any

from cmk.agent_based.v2 import Attributes, InventoryPlugin, InventoryResult, TableRow
from cmk.plugins.prism_v4.agent_based.prism_host_networks_v4 import NicSection
from cmk.plugins.prism_v4.agent_based.prism_vm_nics_v4 import nic_ips
from cmk.plugins.prism_v4.lib_v4 import cluster_version, iso_to_timestamp

Section = Mapping[str, Any]


def _ip(address: Mapping[str, Any] | None) -> str | None:
    return (address or {}).get("ipv4", {}).get("value")


def _ips(addresses: Sequence[Mapping[str, Any]] | None) -> str:
    return ", ".join(ip for a in addresses or [] if (ip := _ip(a) or a.get("fqdn", {}).get("value")))


def inventory_prism_cluster_v4(section: Section) -> InventoryResult:
    config = section.get("config", {})
    network = section.get("network", {})
    software = {s.get("softwareType"): s.get("version") for s in config.get("clusterSoftwareMap", [])}
    fault_tolerance = config.get("faultToleranceState", {})
    yield Attributes(
        path=["software", "applications", "nutanix", "cluster"],
        inventory_attributes={
            "name": section.get("name"),
            "aos_version": cluster_version(section),
            "full_version": config.get("buildInfo", {}).get("fullVersion"),
            "ncc_version": software.get("NCC"),
            "is_lts": config.get("isLts"),
            "cluster_type": config.get("clusterType"),
            "hypervisors": ", ".join(config.get("hypervisorTypes", [])),
            "nodes": section.get("nodes", {}).get("numberOfNodes"),
            "redundancy_factor": config.get("redundancyFactor"),
            "desired_fault_tolerance": fault_tolerance.get("desiredClusterFaultTolerance"),
            "domain_awareness": fault_tolerance.get("domainAwarenessLevel"),
            "timezone": config.get("timezone"),
            "external_ip": _ip(network.get("externalAddress")),
            "data_services_ip": _ip(network.get("externalDataServiceIp")),
            "dns_servers": _ips(network.get("nameServerIpList")),
            "ntp_servers": _ips(network.get("ntpServerIpList")),
            "pulse_enabled": config.get("pulseStatus", {}).get("isEnabled"),
            "remote_support_enabled": config.get("isRemoteSupportEnabled"),
        },
        status_attributes={"upgrade_status": section.get("upgradeStatus")},
    )


inventory_plugin_prism_cluster_v4 = InventoryPlugin(
    name="prism_cluster_v4",
    inventory_function=inventory_prism_cluster_v4,
)


def inventory_prism_host_v4(
    section_prism_host_v4: Section | None,
    section_prism_host_disks_v4: Mapping[str, Mapping[str, Any]] | None,
    section_prism_host_nics_v4: NicSection | None,
) -> InventoryResult:
    if host := section_prism_host_v4:
        hypervisor = host.get("hypervisor", {})
        yield Attributes(
            path=["hardware", "system"],
            inventory_attributes={
                "manufacturer": "Nutanix",
                "product": host.get("blockModel"),
                "serial": host.get("nodeSerial"),
            },
        )
        yield Attributes(
            path=["hardware", "cpu"],
            inventory_attributes={
                "model": host.get("cpuModel"),
                "cpus": host.get("numberOfCpuSockets"),
                "cores": host.get("numberOfCpuCores"),
                "threads": host.get("numberOfCpuThreads"),
                "max_speed": host.get("cpuFrequencyHz"),
            },
        )
        yield Attributes(
            path=["hardware", "memory"],
            inventory_attributes={"total_ram_usable": host.get("memorySizeBytes")},
        )
        full_name = str(hypervisor.get("fullName", ""))
        yield Attributes(
            path=["software", "os"],
            inventory_attributes={
                "vendor": "Nutanix",
                "type": hypervisor.get("type"),
                "name": full_name or None,
                "version": full_name.split()[-1] if full_name else None,
            },
        )
        yield Attributes(
            path=["software", "applications", "nutanix", "node"],
            inventory_attributes={
                "cluster": host.get("cluster", {}).get("name"),
                "block_serial": host.get("blockSerial"),
                "host_type": host.get("hostType"),
                "hypervisor_ip": _ip(hypervisor.get("externalAddress")),
                "cvm_ip": _ip(host.get("controllerVm", {}).get("externalAddress")),
                "ipmi_ip": _ip(host.get("ipmi", {}).get("ip")),
                "secure_boot": host.get("isSecureBooted"),
            },
        )

    for location, disk in (section_prism_host_disks_v4 or {}).items():
        yield TableRow(
            path=["hardware", "storage", "disks"],
            key_columns={"fsnode": location},
            inventory_columns={
                "product": disk.get("model"),
                "vendor": disk.get("vendor"),
                "serial": disk.get("serialNumber"),
                "firmware": disk.get("firmwareVersion"),
                "target_firmware": disk.get("targetFirmwareVersion"),
                "size": disk.get("diskSizeBytes"),
                "type": disk.get("storageTier"),
                "local": True,
            },
        )

    for nic in (section_prism_host_nics_v4.nics.values() if section_prism_host_nics_v4 else []):
        switch_if = next(iter(nic.get("attachedSwitchInterfaceList") or []), {})
        yield TableRow(
            path=["hardware", "nwadapter"],
            key_columns={"name": nic.get("name") or nic.get("macAddress")},
            inventory_columns={
                "type": nic.get("hostDescription"),
                "macaddress": nic.get("macAddress"),
                "speed": int(nic.get("linkCapacityInMbps") or 0) * 1000000 or None,
                "driver": nic.get("driverVersion"),
                "firmware": nic.get("firmwareVersion"),
                "mtu": nic.get("mtuInBytes"),
                "switch": _ip(switch_if.get("switchManagementAddress")),
                "switch_port": switch_if.get("switchInterfaceName"),
            },
        )


inventory_plugin_prism_host_v4 = InventoryPlugin(
    name="prism_host_v4",
    sections=["prism_host_v4", "prism_host_disks_v4", "prism_host_nics_v4"],
    inventory_function=inventory_prism_host_v4,
)


def _guest_os(vm: Section) -> Mapping[str, str | None]:
    """Guest tools report the OS like "windows:64:WindowsServer2022Standard" """
    parts = str(vm.get("guestTools", {}).get("guestOsVersion") or "").split(":")
    if len(parts) != 3:
        return {}
    return {"type": parts[0], "arch": f"{parts[1]} bit", "name": parts[2]}


def inventory_prism_vm_v4(section: Section) -> InventoryResult:
    sockets = int(section.get("numSockets") or 0)
    cores = sockets * int(section.get("numCoresPerSocket") or 1)
    yield Attributes(
        path=["hardware", "cpu"],
        inventory_attributes={
            "cpus": sockets,
            "cores": cores,
            "threads": cores * int(section.get("numThreadsPerCore") or 1),
        },
    )
    yield Attributes(
        path=["hardware", "memory"],
        inventory_attributes={"total_ram_usable": section.get("memorySizeBytes")},
    )
    if guest_os := _guest_os(section):
        yield Attributes(path=["software", "os"], inventory_attributes=guest_os)

    guest_tools = section.get("guestTools", {})
    boot = section.get("bootConfig", {})
    create_time = section.get("createTime")
    yield Attributes(
        path=["software", "applications", "nutanix", "vm"],
        inventory_attributes={
            "machine_type": section.get("machineType"),
            "secure_boot": boot.get("isSecureBootEnabled"),
            "vtpm": section.get("vtpmConfig", {}).get("isVtpmEnabled"),
            "protection_type": section.get("protectionType"),
            "created": int(iso_to_timestamp(create_time)) if create_time else None,
            "description": section.get("description"),
            "guest_tools_version": guest_tools.get("version") if guest_tools.get("isInstalled") else None,
        },
        status_attributes={
            "power_state": section.get("powerState"),
            "host": section.get("hostName"),
        },
    )

    for disk in section.get("disks", []):
        address = disk.get("diskAddress", {})
        backing = disk.get("backingInfo", {})
        yield TableRow(
            path=["hardware", "storage", "disks"],
            key_columns={"fsnode": f"{address.get('busType', 'disk')}.{address.get('index', 0)}"},
            inventory_columns={
                "bus": address.get("busType"),
                "size": backing.get("diskSizeBytes"),
                "type": "Volume group" if "volumeGroupExtId" in backing else "vDisk",
                "local": False,
            },
        )

    for index, nic in enumerate(section.get("nics", [])):
        backing = nic.get("backingInfo") or nic.get("nicBackingInfo") or {}
        network = nic.get("networkInfo") or nic.get("nicNetworkInfo") or {}
        yield TableRow(
            path=["hardware", "nwadapter"],
            key_columns={"name": f"NIC {index}"},
            inventory_columns={
                "type": backing.get("model"),
                "macaddress": backing.get("macAddress"),
                "ipv4_address": ", ".join(nic_ips(nic)) or None,
                "vlan_mode": network.get("vlanMode"),
                "connected": backing.get("isConnected"),
            },
        )


inventory_plugin_prism_vm_v4 = InventoryPlugin(
    name="prism_vm_v4",
    inventory_function=inventory_prism_vm_v4,
)

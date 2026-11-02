#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

from collections.abc import Mapping, Sequence
from typing import Any

from cmk.agent_based.v2 import CheckPlugin, CheckResult, DiscoveryResult, Result, Service, State

Section = Mapping[str, Any]


def _backing_info(nic: Mapping[str, Any]) -> Mapping[str, Any]:
    # API v4.2 renamed backingInfo/networkInfo, both are still delivered
    return nic.get("backingInfo") or nic.get("nicBackingInfo") or {}


def _network_info(nic: Mapping[str, Any]) -> Mapping[str, Any]:
    return nic.get("networkInfo") or nic.get("nicNetworkInfo") or {}


def nic_ips(nic: Mapping[str, Any]) -> Sequence[str]:
    ipv4 = _network_info(nic).get("ipv4Info", {})
    return [ip["value"] for ip in ipv4.get("learnedIpAddresses", []) if "value" in ip]


def describe_nic(nic: Mapping[str, Any]) -> str:
    backing = _backing_info(nic)
    network = _network_info(nic)
    details = [
        f"MAC: {backing.get('macAddress')}",
        f"Model: {backing.get('model', 'unknown')}",
        f"VLAN mode: {network.get('vlanMode', 'unknown')}",
    ]
    if ips := nic_ips(nic):
        details.append(f"IP: {', '.join(ips)}")
    if trunked := network.get("trunkedVlans"):
        details.append(f"Trunked VLANs: {', '.join(map(str, trunked))}")
    return ", ".join(details)


def discovery_prism_vm_nics_v4(section: Section) -> DiscoveryResult:
    if section.get("nics"):
        yield Service()


def check_prism_vm_nics_v4(section: Section) -> CheckResult:
    if not (nics := section.get("nics")):
        return

    running = str(section.get("powerState", "")).upper() == "ON"
    disconnected = [nic for nic in nics if _backing_info(nic).get("isConnected") is False]
    summary = f"{len(nics)} NIC{'s' if len(nics) != 1 else ''}"
    if not disconnected:
        yield Result(state=State.OK, summary=f"{summary}, all connected")
    else:
        yield Result(
            state=State.WARN if running else State.OK,
            summary=(
                f"{summary}, {len(disconnected)} disconnected"
                + ("" if running else " (VM not running)")
            ),
        )
    for nic in nics:
        connected = _backing_info(nic).get("isConnected") is not False
        yield Result(
            state=State.OK,
            notice=f"{'Connected' if connected else 'Disconnected'}: {describe_nic(nic)}",
        )


check_plugin_prism_vm_nics_v4 = CheckPlugin(
    name="prism_vm_nics_v4",
    service_name="NTNX NICs",
    sections=["prism_vm_v4"],
    discovery_function=discovery_prism_vm_nics_v4,
    check_function=check_prism_vm_nics_v4,
)

#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# ported to API v4 by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    RuleSetType,
    State,
    StringTable,
    get_value_store,
    render,
)
from cmk.plugins.lib import interfaces  # type: ignore[import]
from cmk.plugins.prism_v4.lib_v4 import parse_list


def _nic_name(nic: Mapping[str, Any]) -> str:
    if name := nic.get("name"):
        return str(name)
    if mac := nic.get("macAddress"):
        # try to provide stable sorting without name
        return f"unknown_{mac}"
    return "unknown"


def _oper_status(nic: Mapping[str, Any]) -> str:
    """API v4 reports "1" for link up and "0" for link down"""
    if (status := nic.get("interfaceStatus")) is not None:
        return "1" if str(status) == "1" else "2"
    return "1" if nic.get("linkSpeedInKbps") else "2"


@dataclass(frozen=True)
class NicSection:
    interfaces: interfaces.Section[interfaces.InterfaceWithRates]
    # raw NIC data by interface index, for the details the interfaces library doesn't know
    nics: Mapping[str, Mapping[str, Any]]


def parse_prism_host_networks_v4_pure(
    string_table: StringTable,
    timestamp: float,
) -> NicSection:
    nics = sorted(((_nic_name(nic), nic) for nic in parse_list(string_table)), key=lambda x: x[0])
    return NicSection(
        interfaces=[
            interfaces.InterfaceWithRates(
                attributes=interfaces.Attributes(
                    index=str(index),
                    descr=name,
                    alias=name,
                    type="6",
                    speed=int(nic.get("linkSpeedInKbps") or 0) * 1000,
                    oper_status=_oper_status(nic),
                    phys_address=interfaces.mac_address_from_hexstring(
                        nic.get("macAddress") or ""
                    ),
                ),
                # API v4 has no traffic counters for host NICs
                rates=interfaces.Rates(),
                get_rate_errors=[],
                timestamp=timestamp,
            )
            for index, (name, nic) in enumerate(nics)
        ],
        nics={str(index): nic for index, (_name, nic) in enumerate(nics)},
    )


def parse_prism_host_networks_v4(string_table: StringTable) -> NicSection:
    return parse_prism_host_networks_v4_pure(string_table, time.time())


agent_section_prism_host_nics_v4 = AgentSection(
    name="prism_host_nics_v4",
    parse_function=parse_prism_host_networks_v4,
)


def discovery_prism_host_networks_v4(
    params: Sequence[Mapping[str, Any]], section: NicSection
) -> DiscoveryResult:
    yield from interfaces.discover_interfaces(params, section.interfaces)


def _find_nic(item: str, section: NicSection) -> Mapping[str, Any] | None:
    """The item is the index, the name or the alias, depending on the discovery rule"""
    for iface in section.interfaces:
        attributes = iface.attributes
        if item in (attributes.descr, attributes.alias) or (
            item.isdigit() and int(item) == int(attributes.index)
        ):
            return section.nics.get(attributes.index)
    return None


def _check_nic_details(nic: Mapping[str, Any], params: Mapping[str, Any]) -> CheckResult:
    speed_kbps = int(nic.get("linkSpeedInKbps") or 0)
    capacity_mbps = int(nic.get("linkCapacityInMbps") or 0)
    speed_settings = params.get("speed", None)
    if speed_settings and speed_kbps and speed_kbps < speed_settings / 1000:
        yield Result(
            state=State.WARN,
            summary=(
                f"Link speed {render.networkbandwidth(speed_kbps * 125)} below configured "
                f"speed {render.networkbandwidth(speed_settings / 8)}"
            ),
        )
    elif speed_settings and speed_kbps and speed_kbps == speed_settings / 1000:
        yield Result(
            state=State.OK,
            summary=(
                f"Link speed {render.networkbandwidth(speed_kbps * 125)} is configured with "
                f"speed {render.networkbandwidth(speed_settings / 8)}"
            ),
        )
    elif speed_kbps and capacity_mbps and speed_kbps < capacity_mbps * 1000:
        yield Result(
            state=State.WARN,
            summary=(
                f"Link speed {render.networkbandwidth(speed_kbps * 125)} below capacity "
                f"{render.networkbandwidth(capacity_mbps * 125000)}"
            ),
        )
    if (mtu := nic.get("mtuInBytes")) is not None:
        yield Result(state=State.OK, notice=f"MTU: {mtu}")

    for switch_if in nic.get("attachedSwitchInterfaceList") or []:
        switch = (
            switch_if.get("switchManagementAddress", {}).get("ipv4", {}).get("value")
            or nic.get("switchMacAddress")
            or "unknown"
        )
        description = switch_if.get("switchInterfaceDescription")
        yield Result(
            state=State.OK,
            notice=(
                f"Neighbor ({nic.get('discoveryProtocol', 'LLDP')}): switch {switch}"
                + (f" ({nic['switchVendorInfo'].strip()})" if nic.get("switchVendorInfo") else "")
                + f", port {switch_if.get('switchInterfaceName')}"
                + (f" ({description})" if description else "")
            ),
        )


def check_prism_host_networks_v4(
    item: str, params: Mapping[str, Any], section: NicSection
) -> CheckResult:
    yield from interfaces.check_multiple_interfaces(
        item, params, section.interfaces, value_store=get_value_store()
    )
    if (nic := _find_nic(item, section)) is not None:
        yield from _check_nic_details(nic, params)


check_plugin_prism_host_networks_v4 = CheckPlugin(
    name="prism_host_networks_v4",
    service_name="NTNX NIC %s",
    sections=["prism_host_nics_v4"],
    discovery_ruleset_name="inventory_if_rules",
    discovery_ruleset_type=RuleSetType.ALL,
    discovery_default_parameters=dict(interfaces.DISCOVERY_DEFAULT_PARAMETERS),
    check_default_parameters=interfaces.CHECK_DEFAULT_PARAMETERS,
    discovery_function=discovery_prism_host_networks_v4,
    check_function=check_prism_host_networks_v4,
    check_ruleset_name="interfaces",
)

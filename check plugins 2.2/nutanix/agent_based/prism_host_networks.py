#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.
from typing import Any, Dict, Mapping, Sequence

from cmk.base.plugins.agent_based.agent_based_api.v1 import register
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
    StringTable,
)
from cmk.base.plugins.agent_based.utils import interfaces
from .utils.prism import load_json


Section = Dict[str, Mapping[str, Any]]


def parse_prism_host_networks(string_table: StringTable) -> Section:
    parsed: Section = {}
    data = load_json(string_table)
    for element in data:
        parsed.setdefault(element.get("name", "unknown"), element)
    return parsed


register.agent_section(
    name="prism_host_networks",
    parse_function=parse_prism_host_networks,
)


def _create_interface(
    section: Section,
) -> interfaces.Section[interfaces.InterfaceWithRates]:
    return [
        interfaces.InterfaceWithRates(
            attributes=interfaces.Attributes(
                index=str(index),
                descr=name,
                alias=name,
                type=6,
                speed=(
                    0
                    if not raw_stats["link_speed_in_kbps"]
                    else float(raw_stats["link_speed_in_kbps"]) * 1000
                ),
                oper_status=("1" if raw_stats["link_speed_in_kbps"] else "2"),
                phys_address=interfaces.mac_address_from_hexstring(
                    raw_stats.get("mac_address", "")
                ),
            ),
            rates=interfaces.Rates(
                in_octets=float(raw_stats["stats"]["network.received_bytes"]) / 30,
                in_ucast=float(raw_stats["stats"]["network.received_pkts"]) / 30,
                in_mcast=(
                    float(raw_stats["stats"]["network.multicast_received_pkts"]) / 30),
                in_bcast=(
                    float(raw_stats["stats"]["network.broadcast_received_pkts"]) / 30),
                in_disc=float(raw_stats["stats"]["network.dropped_received_pkts"]) / 30,
                in_err=float(raw_stats["stats"]["network.error_received_pkts"]) / 30,
                out_octets=float(raw_stats["stats"]["network.transmitted_bytes"]) / 30,
                out_ucast=float(raw_stats["stats"]["network.transmitted_pkts"]) / 30,
                out_mcast=(
                    float(raw_stats["stats"]["network.multicast_transmitted_pkts"]) / 30),
                out_bcast=(
                    float(raw_stats["stats"]["network.broadcast_transmitted_pkts"]) / 30),
                out_disc=(
                    float(raw_stats["stats"]["network.dropped_transmitted_pkts"]) / 30),
                out_err=(
                    float(raw_stats["stats"]["network.error_transmitted_pkts"]) / 30),
            ),
            get_rate_errors=[],
        )
        for index, (name, raw_stats) in enumerate(sorted(section.items()))
    ]


def discovery_prism_host_networks(
    params: Sequence[Mapping[str, Any]], section: Section
) -> DiscoveryResult:
    yield from interfaces.discover_interfaces(
        params,
        _create_interface(section),
    )


def check_prism_host_networks(
    item: str, params: Mapping[str, Any], section: Section
) -> CheckResult:
    data = section.get(item)
    if not data:
        return

    yield from interfaces.check_multiple_interfaces(
        item,
        params,
        _create_interface(section),
    )


register.check_plugin(
    name="prism_host_networks",
    service_name="NTNX NIC %s",
    sections=["prism_host_networks"],
    discovery_ruleset_name="inventory_if_rules",
    discovery_ruleset_type=register.RuleSetType.ALL,
    discovery_default_parameters=dict(interfaces.DISCOVERY_DEFAULT_PARAMETERS),
    check_default_parameters=interfaces.CHECK_DEFAULT_PARAMETERS,
    discovery_function=discovery_prism_host_networks,
    check_function=check_prism_host_networks,
    check_ruleset_name="if",
)

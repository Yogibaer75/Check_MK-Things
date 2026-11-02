#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    render,
    Result,
    Service,
    State,
)

Section = Mapping[str, Any]


def discovery_prism_vm_network_v4(
    section_prism_vm_v4: Section | None, section_prism_vm_stats_v4: Section | None
) -> DiscoveryResult:
    # the byte counters are also reported for VMs which are powered off
    if section_prism_vm_stats_v4 and "hypervisorNumReceivedBytes" in section_prism_vm_stats_v4:
        yield Service()


def check_prism_vm_network_v4(
    section_prism_vm_v4: Section | None, section_prism_vm_stats_v4: Section | None
) -> CheckResult:
    if not section_prism_vm_stats_v4:
        return

    if str((section_prism_vm_v4 or {}).get("powerState", "")).upper() != "ON":
        yield Result(state=State.OK, summary="VM not running no network check possible")
        return

    # the hypervisor counters are the sums over the sampling interval (about 30s)
    if not (timespan_us := section_prism_vm_stats_v4.get("hypervisorTimespanMicros")):
        yield Result(state=State.UNKNOWN, summary="No sampling interval available")
        return
    timespan = int(timespan_us) / 1000000

    def rate(key: str) -> float:
        return float(section_prism_vm_stats_v4.get(key) or 0) / timespan

    received = rate("hypervisorNumReceivedBytes")
    transmitted = rate("hypervisorNumTransmittedBytes")
    yield Result(
        state=State.OK,
        summary=f"In: {render.iobandwidth(received)}, Out: {render.iobandwidth(transmitted)}",
    )
    yield Metric("net_data_recv", received)
    yield Metric("net_data_sent", transmitted)

    dropped_in = rate("hypervisorNumReceivePacketsDropped")
    dropped_out = rate("hypervisorNumTransmitPacketsDropped")
    if dropped_in or dropped_out:
        yield Result(
            state=State.OK,
            summary=f"Dropped packets: in {dropped_in:.2f}/s, out {dropped_out:.2f}/s",
        )
    yield Metric("if_in_discards", dropped_in)
    yield Metric("if_out_discards", dropped_out)


check_plugin_prism_vm_network_v4 = CheckPlugin(
    name="prism_vm_network_v4",
    service_name="NTNX Network",
    sections=["prism_vm_v4", "prism_vm_stats_v4"],
    discovery_function=discovery_prism_vm_network_v4,
    check_function=check_prism_vm_network_v4,
)

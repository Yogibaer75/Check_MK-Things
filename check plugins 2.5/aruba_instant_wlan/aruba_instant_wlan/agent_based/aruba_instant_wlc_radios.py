#!/usr/bin/env python3
"""Aruba Instant WLAN radio checks."""
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from __future__ import annotations

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    SNMPSection,
    SNMPTree,
    State,
    StringTable,
    any_of,
    startswith,
)

PHYSICAL_AP_SYSOBJECT_ID = ".1.3.6.1.4.1.14823.1.2.87"


def _cluster_services_allowed(sysobject_id: str, ap_count: int) -> bool:
    """Allow cluster data on a physical AP only when it is standalone."""
    is_physical_ap = sysobject_id == PHYSICAL_AP_SYSOBJECT_ID or sysobject_id.startswith(
        f"{PHYSICAL_AP_SYSOBJECT_ID}."
    )
    return not is_physical_ap or ap_count == 1


def normalize_mac(value: str) -> str:
    return value.strip().replace(" ", "").replace(":", "").upper()


def parse_aruba_instant_wlc_radios(
    string_table: list[StringTable],
) -> dict[str, dict[str, str | int]] | None:
    sysobject_table, ap_table, radio_table = string_table
    sysobject_id = sysobject_table[0][0] if sysobject_table and sysobject_table[0] else ""

    if not _cluster_services_allowed(sysobject_id, len(ap_table)):
        return None

    ap_names = {}

    for mac, name in ap_table:
        if mac and name:
            ap_names[normalize_mac(mac)] = name

    radios = {}

    for (
        mac,
        radio_id,
        channel,
        power,
        noise,
        utilization,
        status,
        mode,
    ) in radio_table:
        ap_name = ap_names.get(normalize_mac(mac))

        if not ap_name:
            continue

        item = f"{ap_name} {radio_id}"

        radios[item] = {
            "channel": channel,
            "power": int(power),
            "noise": -abs(int(noise)),
            "utilization": int(utilization),
            "status": int(status),
            "mode": mode,
        }

    return radios


snmp_section_aruba_instant_wlc_radios = SNMPSection(
    name="aruba_instant_wlc_radios",
    detect=any_of(
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.14823.1.2.71"),
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.14823.1.2.87"),
    ),
    fetch=[
        SNMPTree(
            base=".1.3.6.1.2.1.1",
            oids=["2.0"],  # sysObjectID
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.14823.2.3.3.1.2.1.1",
            oids=["1", "2"],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.14823.2.3.3.1.2.2.1",
            oids=["1", "2", "4", "5", "6", "7", "20", "22"],
        ),
    ],
    parse_function=parse_aruba_instant_wlc_radios,
)


def discover_aruba_instant_wlc_radios(
    section: dict[str, dict[str, str | int]],
) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_aruba_instant_wlc_radios(
    item: str,
    section: dict[str, dict[str, str | int]],
) -> CheckResult:
    if item not in section:
        yield Result(
            state=State.UNKNOWN,
            summary="Radio not found in SNMP data",
        )
        return

    radio = section[item]

    status = radio["status"]
    channel = radio["channel"]
    power = radio["power"]
    noise = radio["noise"]
    utilization = radio["utilization"]
    mode = radio["mode"]

    if status == 1:
        state = State.OK
        status_text = "Radio up"
    elif status == 2:
        state = State.CRIT
        status_text = "Radio down"
    else:
        state = State.UNKNOWN
        status_text = f"Unknown radio status: {status}"

    yield Result(
        state=state,
        summary=(
            f"{status_text}, "
            f"Channel: {channel}, "
            f"Power: {power} dBm, "
            f"Utilization: {utilization}%, "
            f"Noise: {noise} dBm, "
            f"Mode: {mode}"
        ),
    )

    yield Metric(
        "channel_utilization",
        utilization,
        boundaries=(0, 100),
    )

    yield Metric(
        "transmit_power",
        power,
    )

    yield Metric(
        "noise_floor",
        noise,
    )


check_plugin_aruba_instant_wlc_radios = CheckPlugin(
    name="aruba_instant_wlc_radios",
    service_name="Radio %s",
    discovery_function=discover_aruba_instant_wlc_radios,
    check_function=check_aruba_instant_wlc_radios,
)

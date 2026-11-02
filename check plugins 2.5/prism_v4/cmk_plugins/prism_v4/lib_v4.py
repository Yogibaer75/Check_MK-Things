#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""Helpers for the checks working on the output of agent_prism_v4 (Nutanix API v4)"""

# mypy: disable-error-code="no-any-return"

import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from cmk.agent_based.v2 import Metric, render, Result, State, StringTable

PrismAPIData = dict[str, Any]

PRISM_POWER_STATES = {
    "on": 0,
    "unknown": 3,
    "off": 1,
    "powering_on": 0,
    "shutting_down": 1,
    "powering_off": 1,
    "pausing": 1,
    "paused": 1,
    "suspending": 1,
    "suspended": 1,
    "resuming": 0,
    "resetting": 1,
    "migrating": 0,
    "undetermined": 3,
}


def load_json_v4(string_table: StringTable) -> Any:
    """Every v4 section is one line of JSON, either an object or a list of objects"""
    try:
        return json.loads(string_table[0][0])
    except (IndexError, json.decoder.JSONDecodeError):
        return None


def parse_object(string_table: StringTable) -> PrismAPIData:
    data = load_json_v4(string_table)
    return data if isinstance(data, dict) else {}


def parse_list(string_table: StringTable) -> list[PrismAPIData]:
    data = load_json_v4(string_table)
    return [e for e in data if isinstance(e, dict)] if isinstance(data, list) else []


def latest_stats(data: Mapping[str, Any] | None) -> PrismAPIData:
    """Reduce a v4 stats object to the newest value of every time series.

    Stats endpoints return every metric as a list of {"timestamp", "value"} items,
    plain values (like extId) are kept as they are."""
    result: PrismAPIData = {}
    for key, value in (data or {}).items():
        if key in ("$objectType", "links"):
            continue
        if isinstance(value, list):
            points = [p for p in value if isinstance(p, dict) and "value" in p]
            if not points:
                continue
            value = max(points, key=lambda p: iso_to_timestamp(p["timestamp"]))["value"]
        result[key] = value
    return result


def parse_stats(string_table: StringTable) -> PrismAPIData:
    """Stats sections as a flat mapping of metric name to its newest value.

    The agent already reduces the time series, but raw API responses (time series,
    optionally wrapped in {"data": ...} or a list of responses) are accepted as well."""
    data = load_json_v4(string_table)
    if isinstance(data, list):
        data = data[0] if len(data) == 1 else None
    if not isinstance(data, dict):
        return {}
    if isinstance(data.get("data"), dict):
        data = data["data"]
    return latest_stats(data)


def parse_by_name(string_table: StringTable, name_key: str = "name") -> dict[str, PrismAPIData]:
    """Turn a list of entities into a mapping from the entity name to the entity"""
    parsed: dict[str, PrismAPIData] = {}
    for element in parse_list(string_table):
        parsed.setdefault(element.get(name_key) or "unknown", element)
    return parsed


def first_value(data: Mapping[str, Any], *keys: str) -> Any:
    """Return the value of the first key present (not None), metric names differ between
    API versions and entity types"""
    for key in keys:
        if (value := data.get(key)) is not None:
            return value
    return None


def iso_to_timestamp(value: str) -> float:
    """Convert an API v4 time like "2026-10-16T10:17:36.055382Z" to a unix timestamp"""
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def _parameter_value(value: Mapping[str, Any]) -> Any:
    """Alert parameters are typed, e.g. {"stringValue": "abc"} or {"intValue": 5}"""
    return next((v for k, v in value.items() if not k.startswith("$")), "")


def alert_message(alert: Mapping[str, Any]) -> str:
    """Message of an alert with the {placeholders} replaced by the alert parameters"""
    context = {
        param["paramName"]: _parameter_value(param.get("paramValue", {}))
        for param in alert.get("parameters", [])
        if "paramName" in param
    }
    message = alert.get("message") or alert.get("title") or ""
    try:
        return message.format(**context)
    except (KeyError, IndexError, ValueError):
        return message


def cluster_version(cluster: Mapping[str, Any]) -> str | None:
    """Extract the AOS version (e.g. 7.5.1.13) from the build info"""
    build_info = cluster.get("config", {}).get("buildInfo", {})
    if match := re.search(r"-(\d+(?:\.\d+)+)-", build_info.get("fullVersion", "")):
        return match.group(1)
    return build_info.get("version")


@dataclass(frozen=True)
class IOKeys:
    """Names of the read/write IO metrics, they differ between entity types"""

    read_iops: str
    write_iops: str
    read_kbps: str
    write_kbps: str
    read_latency_us: str | None = None
    write_latency_us: str | None = None


CONTROLLER_IO_KEYS = IOKeys(
    read_iops="controllerNumReadIops",
    write_iops="controllerNumWriteIops",
    read_kbps="controllerReadIoBandwidthKbps",
    write_kbps="controllerWriteIoBandwidthKbps",
    read_latency_us="controllerAvgReadIoLatencyUsecs",
    write_latency_us="controllerAvgWriteIoLatencyUsecs",
)


def check_io(
    stats: Mapping[str, Any], keys: IOKeys, notice_only: bool = False
) -> Iterable[Result | Metric]:
    """Read/write IOPS, throughput and latency with the standard Checkmk disk metrics.

    The API omits values which are 0, so missing keys count as 0. Bandwidth is
    reported in kB/s and latency in microseconds."""

    def value(key: str | None) -> float:
        return float(stats.get(key) or 0) if key else 0.0

    read_iops, write_iops = value(keys.read_iops), value(keys.write_iops)
    read_bps, write_bps = value(keys.read_kbps) * 1000, value(keys.write_kbps) * 1000
    text = (
        f"Read: {read_iops:.0f} IO/s, {render.iobandwidth(read_bps)}, "
        f"Write: {write_iops:.0f} IO/s, {render.iobandwidth(write_bps)}"
    )
    yield Result(state=State.OK, notice=text) if notice_only else Result(
        state=State.OK, summary=text
    )
    yield Metric("disk_read_ios", read_iops)
    yield Metric("disk_write_ios", write_iops)
    yield Metric("disk_read_throughput", read_bps)
    yield Metric("disk_write_throughput", write_bps)
    if keys.read_latency_us:
        yield Metric("disk_read_latency", value(keys.read_latency_us) / 1000000)
    if keys.write_latency_us:
        yield Metric("disk_write_latency", value(keys.write_latency_us) / 1000000)

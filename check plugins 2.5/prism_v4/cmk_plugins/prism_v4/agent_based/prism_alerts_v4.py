#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# ported to API v4 by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

from collections.abc import Mapping, Sequence
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    StringTable,
    render,
)
from cmk.plugins.prism_v4.lib_v4 import alert_message, iso_to_timestamp, parse_list

Section = Sequence[Mapping[str, Any]]
StringMap = Mapping[str, str]


def parse_prism_alerts_v4(string_table: StringTable) -> Section:
    parsed = []
    for entity in parse_list(string_table):
        if entity.get("isResolved"):
            continue
        parsed.append(
            {
                "timestamp": iso_to_timestamp(entity["creationTime"]),
                "severity": entity.get("severity", "UNKNOWN"),
                "message": alert_message(entity).replace("\n", ", "),
                "source_type": entity.get("sourceEntity", {}).get("type"),
                "acknowledged": bool(entity.get("isAcknowledged")),
            }
        )

    return parsed


agent_section_prism_alerts_v4 = AgentSection(
    name="prism_alerts_v4",
    parse_function=parse_prism_alerts_v4,
)


def severity(name: str) -> tuple[int, int]:
    # first value is for sorting second is the nagios status codes
    return {
        "INFO": (0, 0),
        "WARNING": (1, 1),
        "CRITICAL": (3, 2),
    }.get(name, (2, 3))


def discovery_prism_alerts_v4(section: Section) -> DiscoveryResult:
    """We cannot guess items from alerts, since an empty list of alerts does not mean there are
    no items to monitor"""
    yield Service()


def check_prism_alerts_v4(params: StringMap, section: Section) -> CheckResult:
    valid_alerts = [
        e
        for e in section
        if (not params.get("prism_central_only") or e.get("source_type") == "prism_central_vm")
        and not (params.get("ignore_acknowledged") and e.get("acknowledged"))
    ]

    if not valid_alerts:
        yield Result(state=State.OK, summary="No alerts")
        return

    valid_alerts = sorted(valid_alerts, key=lambda d: d["timestamp"], reverse=True)
    # find the newest alert among those with the highest severity
    immediate_alert = max(valid_alerts, key=lambda x: (severity(x["severity"])[0], x["timestamp"]))

    yield Result(
        state=State(severity(immediate_alert["severity"])[1]),
        summary=f"{len(valid_alerts)} alerts",
    )

    message = immediate_alert["message"]
    state = 1 if "has the following problems" in message else 0  # see werk #7203
    yield Result(
        state=State(state),
        summary=f"Last worst on {render.datetime(immediate_alert['timestamp'])}: '{message}'",
    )

    yield Result(state=State.OK, notice="\nLast 10 Alerts\n")
    for i in valid_alerts[:10]:
        yield Result(state=State.OK, notice=f"{render.datetime(i['timestamp'])}\t{i['message']}")


check_plugin_prism_alerts_v4 = CheckPlugin(
    name="prism_alerts_v4",
    service_name="NTNX Alerts",
    discovery_function=discovery_prism_alerts_v4,
    check_function=check_prism_alerts_v4,
    check_ruleset_name="prism_alerts_v4",
    check_default_parameters={
        "prism_central_only": False,
        "ignore_acknowledged": False,
    },
)

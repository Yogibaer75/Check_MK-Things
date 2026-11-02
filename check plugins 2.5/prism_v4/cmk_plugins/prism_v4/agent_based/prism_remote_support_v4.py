#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# ported to API v4 by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)

Section = Mapping[str, Any]


def discovery_prism_remote_support_v4(section: Section) -> DiscoveryResult:
    if "isRemoteSupportEnabled" in section.get("config", {}):
        yield Service()


_TUNNEL_STATE: dict[bool, str] = {
    True: "Remote Tunnel is enabled",
    False: "Remote Tunnel is disabled",
}


def check_prism_remote_support_v4(params: Mapping[str, Any], section: Section) -> CheckResult:
    target_state = params.get("tunnel_state")
    active_state = bool(section.get("config", {}).get("isRemoteSupportEnabled", False))
    message = _TUNNEL_STATE[active_state]

    if target_state != active_state:
        yield Result(state=State.WARN, summary=message)
    else:
        yield Result(state=State.OK, summary=message)


check_plugin_prism_remote_support_v4 = CheckPlugin(
    name="prism_remote_support_v4",
    service_name="NTNX Remote Tunnel",
    sections=["prism_cluster_v4"],
    check_default_parameters={
        "tunnel_state": False,
    },
    discovery_function=discovery_prism_remote_support_v4,
    check_function=check_prism_remote_support_v4,
    check_ruleset_name="prism_remote_support",
)

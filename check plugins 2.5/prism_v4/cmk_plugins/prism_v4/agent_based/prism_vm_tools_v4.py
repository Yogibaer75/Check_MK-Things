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


def discovery_prism_vm_tools_v4(section: Section) -> DiscoveryResult:
    if section.get("guestTools"):
        yield Service()


def check_prism_vm_tools_v4(params: Mapping[str, Any], section: Section) -> CheckResult:
    install_state = params.get("tools_install")
    enabled_state = params.get("tools_enabled")
    data = section.get("guestTools")
    if not data:
        return

    tool_install = data.get("version") if data.get("isInstalled") else None
    tool_enabled = data.get("isEnabled")

    if tool_install is None and install_state == "installed":
        yield Result(state=State.WARN, summary="No tools installed but should be.")
    elif tool_install is None and install_state == "not_installed":
        yield Result(state=State.OK, summary="No tools installed")
    elif tool_install is not None and install_state == "installed":
        yield Result(state=State.OK, summary=f"Tools with version {tool_install} installed")
    elif install_state == "ignored":
        yield Result(state=State.OK, summary="Tools state are ignored")
    elif tool_install is not None and install_state == "not_installed":
        yield Result(
            state=State.WARN,
            summary=f"Tools with version {tool_install} installed but should not be",
        )

    if tool_enabled and enabled_state == "enabled":
        yield Result(state=State.OK, summary="Tools enabled")
    elif tool_enabled and enabled_state == "disabled":
        message = "Tools enabled, but should be disabled"
        yield Result(state=State.WARN, summary=message)
    elif not tool_enabled and enabled_state == "enabled":
        message = "No tools enabled, but should be enabled"
        yield Result(state=State.WARN, summary=message)
    elif enabled_state == "ignored":
        yield Result(state=State.OK, summary="Tools enable state ignored")
    else:
        message = "No tools enabled"
        yield Result(state=State.OK, summary=message)

    yield from _check_reachability(section, data, enabled_state)

    available = data.get("availableVersion")
    if tool_install is not None and available and available != tool_install:
        yield Result(state=State.OK, summary=f"Update available: {available}")


def _check_reachability(
    section: Section, data: Mapping[str, Any], enabled_state: str | None
) -> CheckResult:
    """The tools have to talk to the CVM, otherwise e.g. VSS snapshots fail. This only
    makes sense for running VMs with installed and enabled tools."""
    if (
        enabled_state == "ignored"
        or not data.get("isInstalled")
        or not data.get("isEnabled")
        or str(section.get("powerState", "")).upper() != "ON"
        or (reachable := data.get("isReachable")) is None
    ):
        return
    if reachable:
        yield Result(state=State.OK, notice="Tools are reachable")
    else:
        yield Result(state=State.WARN, summary="Tools are not reachable from the CVM")


check_plugin_prism_vm_tools_v4 = CheckPlugin(
    name="prism_vm_tools_v4",
    service_name="NTNX VMTools",
    sections=["prism_vm_v4"],
    check_default_parameters={
        "tools_install": "installed",
        "tools_enabled": "enabled",
    },
    discovery_function=discovery_prism_vm_tools_v4,
    check_function=check_prism_vm_tools_v4,
    check_ruleset_name="prism_vm_tools",
)

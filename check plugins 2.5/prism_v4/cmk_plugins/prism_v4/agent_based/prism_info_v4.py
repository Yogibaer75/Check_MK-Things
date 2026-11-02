#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# ported to API v4 by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    HostLabel,
    HostLabelGenerator,
    Result,
    Service,
    State,
)
from cmk.plugins.prism_v4.lib_v4 import cluster_version, parse_object, parse_stats

Section = Mapping[str, Any]


def host_label_prism_cluster_v4(section: Section) -> HostLabelGenerator:
    """Host label function

    Labels:
        cmk/nutanix/object:
            This label is set to either "control_plane" for the host with the special agent, "node"
            for Nutanix nodes or "vm" for VMs hosted in Nutanix.

    """
    yield HostLabel("cmk/nutanix/object", "control_plane")


agent_section_prism_cluster_v4 = AgentSection(
    name="prism_cluster_v4",
    parse_function=parse_object,
    host_label_function=host_label_prism_cluster_v4,
)

# latest value of every cluster metric, used by the cluster CPU/memory/IO checks
agent_section_prism_cluster_stats_v4 = AgentSection(
    name="prism_cluster_stats_v4",
    parse_function=parse_stats,
)


def discovery_prism_info_v4(section: Section) -> DiscoveryResult:
    if section:
        yield Service()


def check_prism_info_v4(section: Section) -> CheckResult:
    if not section:
        return

    summary = (
        f"Name: {section.get('name')}, "
        f"Version: {cluster_version(section)}, "
        f"Nodes: {section.get('nodes', {}).get('numberOfNodes')}"
    )
    yield Result(state=State.OK, summary=summary)


check_plugin_prism_info_v4 = CheckPlugin(
    name="prism_info_v4",
    service_name="NTNX Cluster",
    sections=["prism_cluster_v4"],
    discovery_function=discovery_prism_info_v4,
    check_function=check_prism_info_v4,
)

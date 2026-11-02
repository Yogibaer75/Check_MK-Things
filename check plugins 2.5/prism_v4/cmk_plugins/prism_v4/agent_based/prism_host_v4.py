#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# ported to API v4 by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import AgentSection, HostLabel, HostLabelGenerator, StringTable
from cmk.plugins.prism_v4.lib_v4 import parse_list, parse_object, parse_stats

Section = Mapping[str, Any]


def host_label_prism_host_v4(section: Section) -> HostLabelGenerator:
    """Host label function

    Labels:
        cmk/nutanix/object:
            This label is set to either "control_plane" for the host with the special agent, "node"
            for Nutanix nodes or "vm" for VMs hosted in Nutanix.

        cmk/os_name:
            This label is set to the name of the operating system as reported by the agent as "OSName"

        cmk/os_platform:
            This label is set to the platform as reported by the agent as "OSPlatform". In case
            "OSPlatform" is not set, the value of "AgentOS" is used.

    """
    yield HostLabel("cmk/nutanix/object", "node")
    yield HostLabel("cmk/os_platform", "nutanix")
    yield HostLabel("cmk/os_name", "Nutanix AHV")


agent_section_prism_host_v4 = AgentSection(
    name="prism_host_v4",
    parse_function=parse_object,
    host_label_function=host_label_prism_host_v4,
)

# latest value of every host metric
agent_section_prism_host_stats_v4 = AgentSection(
    name="prism_host_stats_v4",
    parse_function=parse_stats,
)


def parse_prism_host_disks_v4(string_table: StringTable) -> Mapping[str, Mapping[str, Any]]:
    """Disks of this host keyed by their slot (the item of the v2 check)"""
    parsed: dict[str, Mapping[str, Any]] = {}
    for disk in parse_list(string_table):
        location = disk.get("location")
        parsed.setdefault(
            str(location) if location is not None else disk.get("serialNumber", "unknown"), disk
        )
    return parsed


agent_section_prism_host_disks_v4 = AgentSection(
    name="prism_host_disks_v4",
    parse_function=parse_prism_host_disks_v4,
)

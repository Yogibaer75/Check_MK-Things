#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# ported to API v4 by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import AgentSection, HostLabel, HostLabelGenerator
from cmk.plugins.prism_v4.lib_v4 import parse_object, parse_stats

Section = Mapping[str, Any]


def host_label_prism_vm_v4(section: Section) -> HostLabelGenerator:
    """Host label function

    Labels:
        cmk/nutanix/object:
            This label is set to either "control_plane" for the host with the special agent, "node"
            for Nutanix nodes or "vm" for VMs hosted in Nutanix.

    """
    yield HostLabel("cmk/nutanix/object", "vm")


agent_section_prism_vm_v4 = AgentSection(
    name="prism_vm_v4",
    parse_function=parse_object,
    host_label_function=host_label_prism_vm_v4,
)

# newest stats sample of the VM
agent_section_prism_vm_stats_v4 = AgentSection(
    name="prism_vm_stats_v4",
    parse_function=parse_stats,
)

#!/usr/bin/python

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from collections.abc import Mapping
from typing import Any

from cmk_addons.plugins.hyperv.lib import hyperv_vm_convert

from cmk.agent_based.v2 import (  # type: ignore[import]
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)

Section = dict[str, Mapping[str, Any]]


def discovery_hyperv_vm_ram(section) -> DiscoveryResult:
    if "config.hardware.RAMType" in section:
        yield Service()


def check_hyperv_vm_ram(section: Section) -> CheckResult:
    if not section:
        yield Result(state=State(3), summary="RAM information is missing")

    elif section.get("config.hardware.RAMType") == "Dynamic Memory":
        message = (
            f"Dynamic Memory configured with {section.get('config.hardware.MinRAM', 'missing')} MB"
            f" minimum and {section.get('config.hardware.MaxRAM', 'missing')} MB maximum"
            f" - start {section.get('config.hardware.StartRAM', 'missing')} MB"
        )
    else:
        message = (
            f"Static Memory configured with {section.get('config.hardware.RAM', 'missing')} MB"
        )

    yield Result(state=State(0), summary=message)


agent_section_hyperv_vm_ram = AgentSection(
    name="hyperv_vm_ram",
    parse_function=hyperv_vm_convert,
)

check_plugin_hyperv_vm_ram = CheckPlugin(
    name="hyperv_vm_ram",
    service_name="HyperV RAM",
    sections=["hyperv_vm_ram"],
    discovery_function=discovery_hyperv_vm_ram,
    check_function=check_hyperv_vm_ram,
)

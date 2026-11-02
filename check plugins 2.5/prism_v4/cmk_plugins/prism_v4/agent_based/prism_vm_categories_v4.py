#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

from collections.abc import Mapping, Sequence
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
    StringTable,
)
from cmk.plugins.prism_v4.lib_v4 import parse_list

# category name -> assigned values (a VM can have several values of one category)
Section = Mapping[str, Sequence[str]]


def parse_prism_vm_categories_v4(string_table: StringTable) -> Section:
    parsed: dict[str, list[str]] = {}
    for category in parse_list(string_table):
        if (key := category.get("key")) is None:
            continue
        parsed.setdefault(str(key), []).append(str(category.get("value", "")))
    return parsed


def host_label_prism_vm_categories_v4(section: Section) -> HostLabelGenerator:
    """Host label function

    Labels:
        nutanix/category/<category name>:
            This label is set for every Nutanix category assigned to the VM, the label
            value is the category value. If a VM has several values of one category,
            the values are sorted and joined by ",".

    """
    for key, values in section.items():
        yield HostLabel(f"nutanix/category/{key.replace(':', '_')}", ",".join(sorted(values)))


agent_section_prism_vm_categories_v4 = AgentSection(
    name="prism_vm_categories_v4",
    parse_function=parse_prism_vm_categories_v4,
    host_label_function=host_label_prism_vm_categories_v4,
)


def _render(key: str, values: Sequence[str]) -> str:
    return f"{key}: {', '.join(values)}"


def discovery_prism_vm_categories_v4(section: Section) -> DiscoveryResult:
    # also VMs without categories, so missing expected categories can be detected
    yield Service()


def check_prism_vm_categories_v4(params: Mapping[str, Any], section: Section) -> CheckResult:
    if section:
        yield Result(
            state=State.OK,
            summary="; ".join(_render(key, values) for key, values in sorted(section.items())),
        )
    else:
        yield Result(state=State.OK, summary="No categories assigned")

    if not (expected := params.get("expected")):
        return

    state_missing = State(params.get("state_missing", State.WARN.value))
    expected_values: dict[str, set[str] | None] = {}
    for entry in expected:
        key, value = entry["key"], entry.get("value") or None
        if (assigned := section.get(key)) is None or (value is not None and value not in assigned):
            yield Result(
                state=state_missing,
                summary=f"Missing category {key}" + (f": {value}" if value else ""),
            )
        # None means any value of this category is expected
        if value is None:
            expected_values[key] = None
        elif (known := expected_values.setdefault(key, set())) is not None:
            known.add(value)

    state_unexpected = State(params.get("state_unexpected", State.OK.value))
    for key, values in sorted(section.items()):
        if key not in expected_values:
            unexpected = list(values)
        elif (known := expected_values[key]) is None:
            continue
        else:
            unexpected = [v for v in values if v not in known]
        if unexpected:
            yield Result(
                state=state_unexpected,
                summary=f"Unexpected category {_render(key, unexpected)}",
            )


check_plugin_prism_vm_categories_v4 = CheckPlugin(
    name="prism_vm_categories_v4",
    service_name="NTNX Categories",
    sections=["prism_vm_categories_v4"],
    discovery_function=discovery_prism_vm_categories_v4,
    check_function=check_prism_vm_categories_v4,
    check_default_parameters={},
    check_ruleset_name="prism_vm_categories",
)

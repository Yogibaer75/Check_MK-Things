#!/usr/bin/env python3
"""Oracle ILOM problems checks"""
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) https://github.com/meni2029
# some formatting Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from typing import Any, Dict, List

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    OIDEnd,
    Result,
    Service,
    SNMPSection,
    SNMPTree,
    State,
    StringTable,
    contains,
)
from cmk_addons.plugins.oracle_ilom.lib import (
    convert_date_and_time,
)

oracle_ilom_map_subsystem = {
    "1": "None",
    "2": "Cooling",
    "3": "Processors",
    "4": "Memory",
    "5": "Power",
    "6": "Storage",
    "7": "Network",
    "8": "IOModule",
    "9": "Blade",
    "10": "DCU",
    "11": "CPUModule",
    "12": "PCIDevices",
    "13": "ORD",
    "99": "Unknown",
}

# Subsystems to create dedicated checks for
DEDICATED_SUBSYSTEMS = {
    "3": "Processors",
    "4": "Memory",
    "5": "Power",
    "2": "Cooling",
    "6": "Storage",
    "7": "Network",
}

# Reverse mapping for subsystem name to code
SUBSYSTEM_NAME_TO_CODE = {v: k for k, v in DEDICATED_SUBSYSTEMS.items()}
SUBSYSTEM_NAME_TO_CODE["Others"] = "others"


Section = Dict[str, Any]


def parse_oracle_ilom_problems(string_table: List[StringTable]) -> Section:
    """Parse open problems data into dictionary"""
    parsed = {}
    problems_count, problems_table = string_table

    # Parse open problems count
    if problems_count:
        parsed["open_problems_count"] = int(problems_count[0][0])

    # Parse open problems
    problems_by_subsystem = {}
    for entry in problems_table:
        if len(entry) >= 5:
            _index, timestamp, subsystem, location, description = entry[:5]
            if subsystem not in problems_by_subsystem:
                problems_by_subsystem[subsystem] = []
            problems_by_subsystem[subsystem].append(
                {
                    "timestamp": convert_date_and_time(timestamp),
                    "location": location,
                    "description": description,
                }
            )
    parsed["open_problems"] = problems_by_subsystem

    return parsed


snmp_section_oracle_ilom_problems = SNMPSection(
    name="oracle_ilom_problems",
    parse_function=parse_oracle_ilom_problems,
    detect=contains(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.42.2.200"),
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.42.2.2.6.4.1.1",
            oids=[
                "2.0",  # ilomSystemOpenProblemsCount
            ],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.42.2.2.6.4.1.1.10.1",
            oids=[
                OIDEnd(),
                "2",  # ilomSystemOpenProblemTimestamp
                "3",  # ilomSystemOpenProblemSubsystem
                "4",  # ilomSystemOpenProblemLocation
                "5",  # ilomSystemOpenProblemDescription
            ],
        ),
    ],
)


def discover_oracle_ilom_problems(section: Section) -> DiscoveryResult:
    """Unified discovery function for problems - discovers all subsystems"""
    if "open_problems_count" not in section:
        return

    # Discover all subsystems
    for subsystem_name in DEDICATED_SUBSYSTEMS.values():
        yield Service(item=subsystem_name)
    yield Service(item="Others")


def check_oracle_ilom_problems(item: str, section: Section) -> CheckResult:
    """Check status of a specific subsystem"""
    open_problems = section.get("open_problems", {})

    # Item is the subsystem name (e.g., "Processors", "Memory", "Others")
    subsystem_name = item

    if subsystem_name == "Others":
        # Others contains all non-dedicated subsystems
        subsystems_to_check = {
            code: open_problems.get(code, [])
            for code in open_problems.keys()
            if code not in DEDICATED_SUBSYSTEMS
        }
    else:
        # Dedicated subsystem
        subsystem_code = SUBSYSTEM_NAME_TO_CODE.get(subsystem_name)
        if not subsystem_code:
            yield Result(
                state=State.UNKNOWN, summary=f"Unknown subsystem: {subsystem_name}"
            )
            return
        subsystems_to_check = {subsystem_code: open_problems.get(subsystem_code, [])}

    # Count total problems in this subsystem(s)
    total_problems = sum(len(problems) for problems in subsystems_to_check.values())

    if total_problems > 0:
        summary_parts = []
        details = ""

        for subsystem_code, problems in subsystems_to_check.items():
            if problems:
                subsys_name = oracle_ilom_map_subsystem.get(
                    subsystem_code, f"Subsystem {subsystem_code}"
                )
                summary_parts.append(f"{subsys_name}: {len(problems)}")
                details += f"[{subsys_name}]:\n"
                for problem in problems:
                    details += (
                        f"{problem['timestamp']} - "
                        f"{problem['location']} - "
                        f"{problem['description']}\n"
                    )

        summary = ", ".join(summary_parts) if summary_parts else ""
        yield Result(
            state=State.CRIT,
            summary=f"Open problems: {total_problems}{f' ({summary})' if summary else ''}",
            details=details.strip(),
        )
    else:
        yield Result(state=State.OK, summary="No open problems")


check_plugin_oracle_ilom_problems = CheckPlugin(
    name="oracle_ilom_problems",
    sections=["oracle_ilom_problems"],
    service_name="Subsystem %s Status",
    discovery_function=discover_oracle_ilom_problems,
    check_function=check_oracle_ilom_problems,
)

#!/usr/bin/env python3
"""Check for SophosXG current HA state"""

# (c) Matthias Binder 'hds@kpc.de' - K&P Computer Service- und Vertriebs-GmbH
# (c) Andreas Doehler 'andreas.doehler@bechtle.com'
# License: GNU General Public License v2

from typing import Dict

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)

Section = Dict[str, str]


def discover_sophosxg_hastate(section: Section) -> DiscoveryResult:
    """if data is present return a service"""
    if section:
        yield Service()


def check_sophosxg_hastate(section: Section) -> CheckResult:
    """check the current ha state"""
    hastate = section.get("currenthastatus", "99")
    currentappkey = section.get("currentappkey")

    ha_states: Dict[str, tuple[str, int]] = {
        "0": ("Not Applicable", 1),
        "1": ("Auxiliary", 0),
        "2": ("Standalone", 2),
        "3": ("Primary", 0),
        "4": ("Faulty", 2),
        "5": ("Ready", 1),
    }

    ha_state_name, state = ha_states.get(hastate, ("Unknown", 3))

    summarytext = (
        f"HA Current Device State: {ha_state_name}, HA Current App Key: {currentappkey}"
    )

    yield Result(state=State(state), summary=summarytext)


check_plugin_sophosxg_currenthastate = CheckPlugin(
    name="sophosxg_currenthastate",
    sections=["sophosxg_hastate"],
    service_name="HA Current State",
    discovery_function=discover_sophosxg_hastate,
    check_function=check_sophosxg_hastate,
)

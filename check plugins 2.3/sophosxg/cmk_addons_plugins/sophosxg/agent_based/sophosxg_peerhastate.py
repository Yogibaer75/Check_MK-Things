#!/usr/bin/env python3
"""Check for SophosXG peer state"""

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


def discover_sophosxg_peerhastate(section: Section) -> DiscoveryResult:
    """if data is present return a service"""
    if section:
        yield Service()


def check_sophosxg_peerhastate(section: Section) -> CheckResult:
    """check the peer ha state"""
    hastate = section.get("peerhastatus", "99")
    peerappkey = section.get("peerappkey")
    haconfigmode = section.get("haconfigmode")

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
        f"HA Peer Device State: {ha_state_name}, "
        f"HA Peer App Key: {peerappkey}, "
        f"HA Peer Device Config Mode: {haconfigmode}"
    )

    yield Result(state=State(state), summary=summarytext)


check_plugin_sophosxg_peerhastate = CheckPlugin(
    name="sophosxg_peerhastate",
    sections=["sophosxg_hastate"],
    service_name="HA Peer State",
    discovery_function=discover_sophosxg_peerhastate,
    check_function=check_sophosxg_peerhastate,
)

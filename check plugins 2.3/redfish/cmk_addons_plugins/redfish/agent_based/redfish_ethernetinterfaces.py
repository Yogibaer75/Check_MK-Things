#!/usr/bin/env python3

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    render,
)
from cmk_addons.plugins.redfish.lib import (
    RedfishAPIData,
    parse_redfish_multiple,
    redfish_health_state,
)

agent_section_redfish_ethernetinterfaces = AgentSection(
    name="redfish_ethernetinterfaces",
    parse_function=parse_redfish_multiple,
    parsed_section_name="redfish_ethernetinterfaces",
)


def discovery_redfish_ethernetinterfaces(
    params: Mapping[str, Any], section: RedfishAPIData
) -> DiscoveryResult:
    """Discover single interfaces"""
    disc_state = params.get("state")
    for key in section.keys():
        if not section[key].get("Status"):
            continue
        if section[key].get("Status", {}).get("State") in [
            "Absent",
            "Disabled",
            "Offline",
            "UnavailableOffline",
            "StandbyOffline",
        ]:
            continue
        if section[key].get("LinkStatus", "NOLINK") in ["LinkDown"] and disc_state == "up":
            continue
        if section[key].get("LinkStatus", "NOLINK") in ["LinkUp"] and disc_state == "down":
            continue

        yield Service(
            item=section[key]["Id"],
            parameters={
                "discover_speed": section[key].get("SpeedMbps", 0)
                if "SpeedMbps" in section[key]
                else section[key].get("CurrentLinkSpeedMbps", 0),
                "discover_link_status": section[key].get("LinkStatus", "NOLINK"),
            },
        )


def check_redfish_ethernetinterfaces(
    item: str, params: Mapping[str, Any], section: RedfishAPIData
) -> CheckResult:
    """Check single interfaces"""

    if (data := section.get(item)) is None:
        return

    link_status = "Unknown"
    if "LinkStatus" in data:
        link_status = data.get("LinkStatus") if data.get("LinkStatus") else "Down"

    yield Result(state=State.OK, summary=f"Link: {link_status}")

    if (
        params.get("discover_link_status") is not None
        and params.get("discover_link_status") != link_status
    ):
        yield Result(
            state=State(params.get("state_if_link_status_changed", State.CRIT.value)),
            summary=f"Link status changed from {params.get('discover_link_status')} to {link_status}",
        )

    link_speed = 0
    if data.get("CurrentLinkSpeedMbps"):
        link_speed = data.get("CurrentLinkSpeedMbps")
    elif data.get("SpeedMbps"):
        link_speed = data.get("SpeedMbps")
    if link_speed is None:
        link_speed = 0

    factor = 1_000_000
    yield Result(
        state=State.OK, summary=f"Speed: {render.networkbandwidth(link_speed / 8 * factor)}"
    )
    if params.get("discover_speed") is not None and params.get("discover_speed") != link_speed:
        yield Result(
            state=State(params.get("state_if_link_speed_changed", State.WARN.value)),
            summary="Link speed changed from "
            f"{render.networkbandwidth(params.get('discover_speed') / 8 * factor)} "
            f"to {render.networkbandwidth(link_speed / 8 * factor)}",
        )

    mac_addr = ""
    if data.get("AssociatedNetworkAddresses"):
        mac_addr = ", ".join(data.get("AssociatedNetworkAddresses"))
    elif data.get("MACAddress"):
        mac_addr = data.get("MACAddress")

    yield Result(state=State.OK, summary=f"MAC: {mac_addr}")

    if data.get("Status"):
        dev_state, dev_msg = redfish_health_state(data.get("Status", {}))
        yield Result(state=State(dev_state), notice=dev_msg)
    else:
        yield Result(state=State.OK, notice="No known status value found")


check_plugin_redfish_ethernetinterfaces = CheckPlugin(
    name="redfish_ethernetinterfaces",
    service_name="Physical port %s",
    discovery_function=discovery_redfish_ethernetinterfaces,
    discovery_ruleset_name="discovery_redfish_ethernetinterfaces",
    discovery_default_parameters={"state": "updown"},
    check_function=check_redfish_ethernetinterfaces,
    check_default_parameters={
        "state_if_link_status_changed": State.CRIT.value,
        "state_if_link_speed_changed": State.WARN.value,
    },
    check_ruleset_name="check_redfish_ethernetinterfaces",
)

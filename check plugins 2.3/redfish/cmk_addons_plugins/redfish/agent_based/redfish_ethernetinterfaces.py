#!/usr/bin/env python3

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from collections.abc import Mapping
from typing import Any

from cmk_addons.plugins.redfish.lib import (  # type: ignore[import]
    parse_redfish_multiple,
    redfish_health_state,
    RedfishAPIData,
)

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    render,
    Result,
    Service,
    State,
)

agent_section_redfish_ethernetinterfaces: AgentSection = AgentSection(
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


def _render_speed(speed: int) -> str:
    factor = 1_000_000
    return render.networkbandwidth(speed / 8 * factor)


def check_redfish_ethernetinterfaces(
    item: str, params: Mapping[str, Any], section: RedfishAPIData
) -> CheckResult:
    """Check single interfaces"""
    data = section.get(item, None)
    if data is None:
        return

    link_state = State.OK
    link_summary = "Link: No info"
    if (link_status := data.get("LinkStatus")) is not None:
        link_summary=f"Link: {link_status}"
        if (discover_link_changed := params.get("discover_link_status")) != link_status:
            link_state=State(params.get("state_if_link_status_changed") or 0)
            link_summary=f"Link: {link_status} (changed from {discover_link_changed})"
    yield Result(state=link_state, summary=link_summary)

    speed_state = State.OK
    speed_summary = "Speed: No info"
    link_speed: int | None = data.get("CurrentLinkSpeedMbps")
    if link_speed is None: # Prioritize CurrentLinkSpeedMbps, fallback to SpeedMbps
        link_speed = data.get("SpeedMbps")

    if link_speed is not None:
        speed_summary = f"Speed: {_render_speed(link_speed)}"
        if (discover_speed := params.get("discover_speed") or 0) != link_speed:
            speed_state = State(params.get("state_if_link_speed_changed") or 0)
            speed_summary = (
                f"Speed: {_render_speed(link_speed)} "
                f"(changed from {_render_speed(discover_speed)})"
            )
    yield Result(state=speed_state, summary=speed_summary)

    mac_addr = None
    if data.get("AssociatedNetworkAddresses"):
        mac_addr = ", ".join(data.get("AssociatedNetworkAddresses"))
    elif data.get("MACAddress"):
        mac_addr = data.get("MACAddress")
    if mac_addr:
        yield Result(state=State.OK, summary=f"MAC Address: {mac_addr}")

    if data.get("Status"):
        dev_state, dev_msg = redfish_health_state(data.get("Status", {}))
        status = dev_state
        message = dev_msg
    else:
        status = 0
        message = "No known status value found"

    yield Result(state=State(status), summary=message)


check_plugin_redfish_ethernetinterfaces = CheckPlugin(
    name="redfish_ethernetinterfaces",
    service_name="Physical port %s",
    sections=["redfish_ethernetinterfaces"],
    discovery_function=discovery_redfish_ethernetinterfaces,
    discovery_ruleset_name="discovery_redfish_ethernetinterfaces",
    discovery_default_parameters={"state": "updown"},
    check_function=check_redfish_ethernetinterfaces,
    check_default_parameters={},
    check_ruleset_name="check_redfish_ethernetinterfaces",
)

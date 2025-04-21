#!/usr/bin/env python3
"""Check for Extreme HiPath WLC APs"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from typing import Any, Dict, List, Mapping, NamedTuple, Optional

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    InventoryPlugin,
    InventoryResult,
    Result,
    Service,
    SNMPSection,
    SNMPTree,
    State,
    StringTable,
    TableRow,
    any_of,
    startswith,
)


class WLCAp(NamedTuple):
    """Dataclass for APs"""

    status: str
    home_state: str
    ip_addr: str
    registration: str
    zone: str
    hw_ver: str
    sw_ver: str
    serial: str
    location: str
    clients: str


Section = Dict[str, WLCAp]


def parse_extreme_wlc_aps(string_table: List[StringTable]) -> Section:
    """parse data into dataclass"""
    client_dict = {}
    for element in string_table[1]:
        wlanap = str(element[0])
        if wlanap in client_dict:
            client_dict[wlanap] += 1
        else:
            client_dict[wlanap] = 1
    wlc_dict = {
        ap_name: WLCAp(
            status=ap_status,
            registration=ap_unprovisioned,
            ip_addr=ap_ip,
            zone=ap_zone,
            hw_ver=ap_hwversion,
            serial=ap_serial,
            location=ap_sysloc,
            sw_ver=ap_swversion,
            home_state=ap_homestate,
            clients=client_dict.get(ap_name, 0),
        )
        for (
            ap_name,
            ap_status,
            ap_unprovisioned,
            ap_ip,
            ap_zone,
            ap_hwversion,
            ap_serial,
            ap_sysloc,
            ap_homestate,
            ap_swversion,
        ) in string_table[0]
    }
    return wlc_dict


DETECT_EXTREM_WLC = any_of(
    startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.4329.15"),
    startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1916.2.294"),
)


snmp_section_extreme_wlc_aps = SNMPSection(
    name="extreme_wlc_aps",
    parse_function=parse_extreme_wlc_aps,
    detect=DETECT_EXTREM_WLC,
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.4329.15.3.5.1.2.1",
            oids=[
                "2",  # Name
                "22",  # Status
                "23",  # Unprovisioned
                "14",  # IpAddress
                "33",  # Zone
                "17",  # HWVersion
                "4",  # SerialNumber
                "30",  # Location
                "20",  # HomeState
                "7",  # SWVersion
            ],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.4329.15.3.6.2.1",
            oids=[
                "12",  # AP Client is connected to
            ],
        ),
    ],
)

# AP Name       .1.3.6.1.4.1.4329.15.3.5.1.2.1.2
# AP Serial     .1.3.6.1.4.1.4329.15.3.5.1.2.1.4
# AP HomeState  .1.3.6.1.4.1.4329.15.3.5.1.2.1.20   local(1),foreign(2)
# AP State      .1.3.6.1.4.1.4329.15.3.5.1.2.1.22   active(1),inactive(2)
# AP Reg State  .1.3.6.1.4.1.4329.15.3.5.1.2.1.22   approved(1),pending(2)
# AP SW Version .1.3.6.1.4.1.4329.15.3.5.1.2.1.7
# AP AddAssign  .1.3.6.1.4.1.4329.15.3.5.1.2.1.12   dhcp(1),static(2)
# AP IP         .1.3.6.1.4.1.4329.15.3.5.1.2.1.14
# AP HW Version .1.3.6.1.4.1.4329.15.3.5.1.2.1.17
# AP Location   .1.3.6.1.4.1.4329.15.3.5.1.2.1.30
# AP Zone       .1.3.6.1.4.1.4329.15.3.5.1.2.1.33
# AP SecureTun  .1.3.6.1.4.1.4329.15.3.5.1.2.1.41
# AP SSH enab   .1.3.6.1.4.1.4329.15.3.5.1.2.1.43
translate_ap_state = {
    "state_1": (0, "up"),
    "state_2": (2, "down"),
    "state_3": (3, "ignore"),
}

def discover_extreme_wlc_aps(section: Section) -> DiscoveryResult:
    """generate one service for every AP in section"""
    for ap_name, _ap_data in section.items():
        yield Service(item=ap_name)


def check_extreme_wlc_aps(item: str, params: Mapping[str, Any], section: Optional[Section]) -> CheckResult:
    """check the state of a single AP"""
    if not section:
        return
    wanted_state, _wanted_state_text = translate_ap_state.get(params.get("state", "state_1"), (0, "up"))
    ap_data = section.get(item)
    if not ap_data:
        return

    map_state = {
        1: (0, "up"),
        2: (2, "down"),
    }
    map_home = {
        "1": "local",
        "2": "foreign",
    }
    ap_state = max(int(ap_data.status), wanted_state)
    state, state_readable = map_state[ap_state]
    if int(ap_data.status) == wanted_state:
        state = 0
    yield Result(state=State(state), summary=f"Status: {state_readable}")

    if ap_data.clients:
        yield Result(state=State(0), summary=f", Clients: {ap_data.clients}")
    if ap_data.zone:
        yield Result(state=State(0), summary=f", Zone: {ap_data.zone}")
    if ap_data.location:
        yield Result(state=State(0), summary=f", System location: {ap_data.location}")
    if ap_data.home_state:
        yield Result(state=State(0), summary=f", Home state: {map_home[ap_data.home_state]}")
    if ap_data.registration == "2":
        yield Result(
            state=State.WARN,
            summary="Registration pending: yes",
        )


def cluster_check_extreme_wlc_aps(
    item: str, params: Mapping[str, Any], section: Mapping[str, Optional[Section]]
) -> CheckResult:
    """Cluster check function"""
    found = []
    for node, node_section in section.items():
        results = list(check_extreme_wlc_aps(item, params, node_section))
        if results:
            found.append((node, results[0]))

    if not found:
        yield Result(state=State(3), summary="AP not found on any controller")
        return

    best_state = State.best(*(result.state for _node, result in found))
    best_running_on, best_result = [(n, r) for n, r in found if r.state == best_state][
        -1
    ]

    yield best_result
    if best_running_on and best_state != State.CRIT:
        yield Result(state=best_state, summary=f"associated on: {best_running_on}")


check_plugin_extreme_wlc_aps = CheckPlugin(
    name="extreme_wlc_aps",
    service_name="AP %s",
    discovery_function=discover_extreme_wlc_aps,
    check_function=check_extreme_wlc_aps,
    cluster_check_function=cluster_check_extreme_wlc_aps,
    check_ruleset_name="extreme_wlc_aps",
    check_default_parameters={
        "state": "state_1",
        "location": "both",
    }
)


def inventory_extreme_wlc_aps(section: Section) -> InventoryResult:
    """Hardware inventory for the AP data"""
    path = ["networking", "wlan", "controller", "accesspoints"]
    for ap_name, ap_data in section.items():
        yield TableRow(
            path=path,
            key_columns={"name": ap_name},
            inventory_columns={
                "ip_addr": ap_data.ip_addr,
                "group": ap_data.zone,
                "model": ap_data.hw_ver,
                "serial": ap_data.serial,
                "sys_location": ap_data.location,
            },
        )


inventory_plugin_extreme_wlc_aps = InventoryPlugin(
    name="extreme_wlc_aps",
    inventory_function=inventory_extreme_wlc_aps,
)

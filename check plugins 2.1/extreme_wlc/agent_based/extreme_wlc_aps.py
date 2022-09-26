#!/usr/bin/env python3

from typing import Dict, NamedTuple, Mapping, List, Optional

from .agent_based_api.v1 import register, Result, Service, SNMPTree, State, TableRow, startswith, any_of
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, InventoryResult, StringTable


class WLCAp(NamedTuple):
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
    client_dict = {}
    for element in string_table[1]:
        wlanap = str(element[0])
        if wlanap in client_dict.keys():
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
            ap_swversion
        ) in string_table[0]
    }
    return wlc_dict

DETECT_EXTREM_WLC = any_of(
    startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.4329.15"),
    startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1916.2.294")
)


register.snmp_section(
    name="extreme_wlc_aps",
    parse_function=parse_extreme_wlc_aps,
    detect=DETECT_EXTREM_WLC,
    fetch=[
      SNMPTree(
        base=".1.3.6.1.4.1.4329.15.3.5.1.2.1",
        oids=[
            "2",   # Name
            "22",  # Status
            "23",  # Unprovisioned
            "14",  # IpAddress
            "33",  # Zone
            "17",  # HWVersion
            "4",   # SerialNumber
            "30",  # Location
            "20",  # HomeState
            "7",   # SWVersion
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

# AP Name	    .1.3.6.1.4.1.4329.15.3.5.1.2.1.2
# AP Serial	    .1.3.6.1.4.1.4329.15.3.5.1.2.1.4
# AP HomeState	.1.3.6.1.4.1.4329.15.3.5.1.2.1.20   local(1),foreign(2)
# AP State	    .1.3.6.1.4.1.4329.15.3.5.1.2.1.22   active(1),inactive(2)
# AP Reg State	.1.3.6.1.4.1.4329.15.3.5.1.2.1.22   approved(1),pending(2)
# AP SW Version .1.3.6.1.4.1.4329.15.3.5.1.2.1.7
# AP AddAssign	.1.3.6.1.4.1.4329.15.3.5.1.2.1.12   dhcp(1),static(2)
# AP IP		    .1.3.6.1.4.1.4329.15.3.5.1.2.1.14
# AP HW Version .1.3.6.1.4.1.4329.15.3.5.1.2.1.17
# AP Location	.1.3.6.1.4.1.4329.15.3.5.1.2.1.30
# AP Zone	    .1.3.6.1.4.1.4329.15.3.5.1.2.1.33
# AP SecureTun  .1.3.6.1.4.1.4329.15.3.5.1.2.1.41
# AP SSH enab   .1.3.6.1.4.1.4329.15.3.5.1.2.1.43

def discover_extreme_wlc_aps(section: Section) -> DiscoveryResult:
    for ap_name, ap_data in section.items():
        yield Service(item=ap_name)


def check_extreme_wlc_aps(item: str, section: Optional[Section]) -> CheckResult:
    if not section:
        return

    if item not in section:
        return

    map_state = {
        "1": (0, "up"),
        "2": (2, "down"),
    }
    map_home = {
        "1": "local",
        "2": "foreign",
    }
    ap_data = section[item]
    state, state_readable = map_state[ap_data.status]
    infotext = "Status: %s" % state_readable
    if ap_data.clients:
        infotext += ", Clients: %s" % ap_data.clients
    if ap_data.zone:
        infotext += ", Zone: %s" % ap_data.zone
    if ap_data.location:
        infotext += ", System location: %s" % ap_data.location
    if ap_data.home_state:
        infotext += ", Home state: %s" % map_home[ap_data.home_state]
    yield Result(
        state=State(state),
        summary=infotext,
    )

    if ap_data.registration == "2":
        yield Result(
            state=State.WARN,
            summary="Registration pending: yes",
        )


def cluster_check_extreme_wlc_aps(item: str, section: Mapping[str, Optional[Section]]) -> CheckResult:
    found = []
    for node, node_section in section.items():
        results = list(check_extreme_wlc_aps(item, node_section))
        if results:
            found.append((node, results[0]))

    if not found:
        yield Result(state=State(3), summary="AP not found on any controller")
        return

    best_state = State.best(*(result.state for _node, result in found))
    best_running_on, best_result = [(n, r) for n, r in found if r.state == best_state][-1]

    yield best_result
    if best_running_on and best_state != State.CRIT:
        yield Result(state=best_state, summary="associated on: %s" % best_running_on)


register.check_plugin(
    name="extreme_wlc_aps",
    service_name="AP %s",
    discovery_function=discover_extreme_wlc_aps,
    check_function=check_extreme_wlc_aps,
    cluster_check_function=cluster_check_extreme_wlc_aps,
)


def inventory_extreme_wlc_aps(section: Section) -> InventoryResult:
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


register.inventory_plugin(
    name="extreme_wlc_aps",
    inventory_function=inventory_extreme_wlc_aps,
)

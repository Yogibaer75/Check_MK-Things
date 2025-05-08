#!/usr/bin/env python3
'''Aruba instant WLC AP check'''
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from typing import NamedTuple
import time
from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    check_levels,
    DiscoveryResult,
    get_value_store,
    Result,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    State,
    StringTable,
    startswith,
)
from cmk.plugins.lib import uptime
from cmk.plugins.lib.cpu_util import check_cpu_util


class WLCAp(NamedTuple):
    """named tuple definition"""

    status: str
    ip_addr: str
    model: str
    serial: str
    role: str
    uptime: int
    memfree: int
    memtotal: int
    cpuutil: int


Section = dict[str, WLCAp]


def parse_aruba_instant_wlc_aps(string_table: StringTable) -> Section:
    """parse data into named tuple"""
    return {
        ap_name: WLCAp(
            status=ap_status,
            ip_addr=ap_ip,
            model=ap_model,
            serial=ap_serial,
            role=ap_role,
            uptime=int(ap_uptime),
            memfree=int(ap_memfree),
            memtotal=int(ap_memtotal),
            cpuutil=int(ap_cpuutil),
        )
        for (
            ap_name,
            ap_status,
            ap_ip,
            ap_model,
            ap_serial,
            ap_role,
            ap_uptime,
            ap_memfree,
            ap_memtotal,
            ap_cpuutil,
        ) in string_table
    }


snmp_section_aruba_instant_wlc_aps = SimpleSNMPSection(
    name="aruba_instant_wlc_aps",
    parse_function=parse_aruba_instant_wlc_aps,
    detect=startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.14823.1.2.111"),
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.14823.2.3.3.1.2.1.1",
        oids=[
            "2",  # aiAPName
            "11",  # aiAPStatus
            "3",  # aiAPIpAddress
            "6",  # aiAPModelName
            "4",  # aiAPSerialNumber
            "13",  # aiAPRole
            "9",  # aiAPUptime
            "8",  # aiAPMemfree
            "10",  # aiAPMemtotal
            "7",  # aiAPCPUUtil
        ],
    ),
)


def discover_aruba_instant_wlc_aps(section: Section) -> DiscoveryResult:
    """one service per AP"""
    for ap_name, ap_data in section.items():
        if ap_data.status == "1":
            yield Service(item=ap_name)


def check_aruba_instant_wlc_aps(item: str, section: Section) -> CheckResult:
    """check state of AP"""
    if item not in section:
        return

    map_state = {
        "1": (0, "up"),
        "2": (2, "down"),
    }
    ap_data = section[item]

    state, state_readable = map_state[ap_data.status]
    infotext = f"Status: {state_readable}"
    yield Result(
        state=State(state),
        summary=infotext,
    )
    if ap_data.uptime:
        yield from uptime.check({}, uptime.Section(float(ap_data.uptime) / 100, None))

    if ap_data.cpuutil:
        yield from check_cpu_util(
            util=ap_data.cpuutil,
            params={"util": (80.0, 90.0)},
            this_time=time.time(),
            value_store=get_value_store(),
        )
    if ap_data.memtotal and ap_data.memfree:
        memused = 100 - (ap_data.memfree / (ap_data.memtotal / 100))
        yield from check_levels(
            memused,
            levels_upper=("fixed", (90.0, 95.0)),
            metric_name="perc",
            label="Memory used",
            render_func=lambda v: f"{v:.1f}%",
            boundaries=(0, 100),
        )


check_plugin_aruba_instant_wlc_aps = CheckPlugin(
    name="aruba_instant_wlc_aps",
    service_name="AP %s",
    discovery_function=discover_aruba_instant_wlc_aps,
    check_function=check_aruba_instant_wlc_aps,
)

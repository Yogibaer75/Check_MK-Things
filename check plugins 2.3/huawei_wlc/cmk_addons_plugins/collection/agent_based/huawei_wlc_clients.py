#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from typing import List

from cmk.agent_based.v2 import (
    OIDEnd,
    SNMPSection,
    SNMPTree,
    StringTable,
    startswith,
)
from cmk.plugins.lib.wlc_clients import ClientsTotal, WlcClientsSection


def parse_huawei_wlc_clients(string_table: List[StringTable]) -> WlcClientsSection[ClientsTotal]:
    section: WlcClientsSection[ClientsTotal] = WlcClientsSection()
    tmp_clients = {}
    sum_clients = 0
    clients = string_table[0]
    all_sids = string_table[1]
    for _index, ssid_name in clients:
        if ssid_name in tmp_clients:
            tmp_clients[ssid_name] += 1
        else:
            tmp_clients[ssid_name] = 1
        sum_clients += 1

    for _index, ssid_name in all_sids:
        if ssid_name not in tmp_clients:
            tmp_clients[ssid_name] = 0

    section.total_clients = sum_clients
    for key in tmp_clients:
        section.clients_per_ssid[key] = ClientsTotal(total=tmp_clients[key])
    return section

snmp_section_huawei_wlc_clients = SNMPSection(
    name="huawei_wlc_clients",
    parsed_section_name="wlc_clients",
    detect=startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.2011.2.240.4"),
    parse_function=parse_huawei_wlc_clients,
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.2011.6.139.18.1.2.1",
            oids=[
                OIDEnd(),
                "18",
            ],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.2011.6.139.17.1.1.1",
            oids=[
                OIDEnd(),
                "4",
            ],
        ),
    ],
)


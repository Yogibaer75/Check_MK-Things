#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Matthias Binder 'hds@kpc.de'
# Rework: Andreas Doehler 'andreas.doehler@bechtle.com'
# License: GNU General Public License

from typing import Dict, Optional
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    all_of,
    exists,
    register,
    startswith,
    Result,
    Service,
    SNMPTree,
    State,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
    StringTable,
)

Section = Dict[str, Dict[str, str]]


def parse_sophosxg_srv(string_table: StringTable) -> Optional[Section]:
    """parse raw snmp data to dictionary"""
    srv_table: list[str] = [
        "POP3",
        "IMAP4",
        "SMTP",
        "FTP",
        "HTTP",
        "AV",
        "AS",
        "DNS",
        "HA",
        "IPS",
        "Apache",
        "NTP",
        "Tomcat",
        "SSL-VPN",
        "IPSec-VPN",
        "Database",
        "Network",
        "Garner",
        "DRouting",
        "SSHd",
        "DGD",
    ]
    try:
        parsed = {}
        for x in range(21):
            parsed.setdefault(srv_table[x], {"state": string_table[x][0]})
        return parsed
    except IndexError:
        return {}


register.snmp_section(
    name="sophosxg_srv",
    parse_function=parse_sophosxg_srv,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.2604.5.1",
        oids=[
            "3",
        ],
    ),
    detect=all_of(
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.2604.5"),
        exists(".1.3.6.1.4.1.2604.5.1.1.*"),
    ),
)


def discover_sophosxg_srv(section: Section) -> DiscoveryResult:
    """every key of the parsed data is creating one service"""
    for key in section.keys():
        yield Service(item=key)


def check_sophosxg_srv(item: str, params: Dict[str, str], section: Section) -> CheckResult:
    """check the service state of single items"""
    data = section.get(item)
    if not data:
        return

    srv_state: Dict[str, tuple[str, int]] = {
        "0": ("untouched", 1),
        "1": ("stopped", 2),
        "2": ("initializing", 1),
        "3": ("running", 0),
        "4": ("exiting", 1),
        "5": ("dead", 2),
        "6": ("frozen", 2),
        "7": ("unregistered", 1),
        "99": ("unknown", 3),
    }

    wanted_state = params.get("state", "99")

    srvtext, srvstate = srv_state.get(data.get("state", "99"), ("unknown", 3))

    if data.get("state") == wanted_state:
        yield Result(state=State.OK, summary=f"Current state is {srvtext}")
    else:
        if wanted_state != "99":
            summarytext = (
                f"Current state is {srvtext} - wanted state was "
                f"{srv_state.get(wanted_state,('unknown', 3))[0]}"
            )
            yield Result(
                state=State(srvstate),
                summary=summarytext,
            )
        else:
            yield Result(
                state=State.OK,
                summary=f"Current state is {srvtext} - no preference selected",
            )


register.check_plugin(
    name="sophosxg_srv",
    service_name="Service %s",
    discovery_function=discover_sophosxg_srv,
    check_function=check_sophosxg_srv,
    check_default_parameters={
        "state": "3",
    },
    check_ruleset_name="sophosxg_srv",
)

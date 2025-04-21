#!/usr/bin/env python3
"""Check for SophosXG service"""

# (c) Matthias Binder 'hds@kpc.de' - K&P Computer Service- und Vertriebs-GmbH
# (c) Andreas Doehler 'andreas.doehler@bechtle.com'
# License: GNU General Public License v2

from typing import Dict, Optional

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    State,
    StringTable,
    all_of,
    exists,
    startswith,
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


snmp_section_sophosxg_srv = SimpleSNMPSection(
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


def check_sophosxg_srv(
    item: str, params: Dict[str, str], section: Section
) -> CheckResult:
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

    rule_state = {
        "untouched": "0",
        "stopped": "1",
        "initializing": "2",
        "running": "3",
        "exiting": "4",
        "dead": "5",
        "frozen": "6",
        "unregistered": "7",
        "unknown": "99",
    }

    wanted_state = rule_state.get(params.get("state", "unknown"), "99")

    srvtext, srvstate = srv_state.get(data.get("state", "99"), ("unknown", 3))

    if data.get("state") == wanted_state:
        yield Result(state=State.OK, summary=f"Current state is {srvtext}")
    else:
        if wanted_state != "99":
            summarytext = (
                f"Current state is {srvtext} - wanted state was "
                f"{srv_state.get(wanted_state, ('unknown', 3))[0]}"
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


check_plugin_sophosxg_srv = CheckPlugin(
    name="sophosxg_srv",
    service_name="Service %s",
    discovery_function=discover_sophosxg_srv,
    check_function=check_sophosxg_srv,
    check_default_parameters={
        "state": "running",
    },
    check_ruleset_name="sophosxg_srv",
)

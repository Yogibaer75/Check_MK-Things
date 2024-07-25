#!/usr/bin/env python3
"""check for Fortigate update status"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

import time
from typing import Optional, Dict, Any
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    DiscoveryResult,
    CheckResult,
    StringTable,
)
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    render,
    register,
    Result,
    Service,
    SNMPTree,
    State,
    startswith,
)

Section = Dict[str, Any]


def parse_fortigate_update(string_table: StringTable) -> Optional[Section]:
    """parse raw snmp data to dictionary"""
    fields = [
        "component",
        "license",
        "version",
        "last_update",
        "update_typ",
        "last_contact",
        "last_result",
    ]
    try:
        parsed = {}
        for line in string_table:
            parsed[line[0]] = {fields[i]: line[i] for i in range(len(fields))}
        return parsed
    except IndexError:
        return {}


def discover_fortigate_update(section: Section) -> DiscoveryResult:
    """every key of the parsed data is found as a service"""
    for key in section:
        if not key:
            continue
        if section[key]["license"] != "n/a":
            yield Service(item=key)


def check_fortigate_update(item, params, section: Section) -> CheckResult:
    """check the age of the single updates"""
    def parse_date(value):
        if value == "n/a":
            return 0, time.time()
        t = time.strptime(value, "%a %b %d %H:%M:%S %Y")
        ts = time.mktime(t)
        return ts, time.time() - ts

    data = section.get(item)
    if not data:
        return

    warn, crit = params["levels"]
    update, update_age = parse_date(data["last_update"])
    message = f"Last update {render.date(update)}"
    contact, _contact_diff = parse_date(data["last_contact"])
    if data["update_typ"] == "manual":
        update_typ = "manual (!)"
    else:
        update_typ = data["update_typ"]

    addon_msg = (f" Update typ: {update_typ} - Version: {data['version']} - "
                 f"Last contact: {render.date(contact)} - Last result: {data['last_result']}")

    if params.get("no_levels"):
        yield Result(state=State.OK, summary= message + " no Levels (!)" + addon_msg)
    elif update_age > crit * 3600 * 24:
        message += (f" (Warn/Crit: {render.timespan(warn * 3600 * 24)}"
                    f"/{render.timespan(crit * 3600 * 24)})")
        yield Result(state=State.CRIT, summary= message + addon_msg)
    elif update_age > warn * 3600 * 24:
        message += (f" (Warn/Crit: {render.timespan(warn * 3600 * 24)}"
                    f"/{render.timespan(crit * 3600 * 24)})")
        yield Result(state=State.WARN, summary= message + addon_msg)
    else:
        yield Result(state=State.OK, summary= message + addon_msg)


register.snmp_section(
    name="fortigate_update",
    parse_function=parse_fortigate_update,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.12356.101.4.6.3.2.2.1",
        oids=[
            "1",  # License Version description
            "2",  # License
            "3",  # Version
            "4",  # License Version update time
            "5",  # License Version update method
            "6",  # License Version try time
            "7",  # License Version try result
        ],
    ),
    detect=startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.12356.101.1")
)

register.check_plugin(
    name="fortigate_update",
    service_name="Component %s",
    discovery_function=discover_fortigate_update,
    check_function=check_fortigate_update,
    check_default_parameters={"levels": (30, 90)},
    check_ruleset_name="fortigate_update",
)

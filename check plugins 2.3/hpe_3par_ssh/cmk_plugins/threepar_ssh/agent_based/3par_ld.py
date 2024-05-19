#!/usr/bin/env python3
"""check for HPE 3Par ld status"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

# Example output from agent:
# <<<3par_ld>>>
#  0 admin.usr.0      1 normal           0/1     5120     5120 V       0  ---     N    Y
#  1 admin.usr.1      1 normal           1/0     5120     5120 V       0  ---     N    Y

# The names of the columns are:
# Id Name          RAID -Detailed_State- Own   SizeMB   UsedMB Use  Lgct LgId WThru MapV

from typing import Mapping
from attr import dataclass
from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    StringTable,
)


@dataclass(frozen=True)
class ThreeParLD:
    """one ld"""

    name: str
    raid: str
    state: str
    owner: str
    size_mb: str
    used_mb: str
    useing: str
    lgct: str
    lgid: str
    wthru: str
    mapv: str


Section = Mapping[str, ThreeParLD]


def parse_3par_ld(string_table: StringTable) -> Section:
    """parse raw data into dict"""
    parsed: dict[str, ThreeParLD] = {}
    for line in string_table:
        if len(line) == 12 and line[0].isdigit():
            for (
                ld_id,
                name,
                raid,
                state,
                owner,
                size_mb,
                used_mb,
                useing,
                lgct,
                lgid,
                wthru,
                mapv,
            ) in line:
                parsed.setdefault(
                    ld_id,
                    ThreeParLD(
                        name,
                        raid,
                        state,
                        owner,
                        size_mb,
                        used_mb,
                        useing,
                        lgct,
                        lgid,
                        wthru,
                        mapv,
                    ),
                )
    return parsed


agent_section_3par_ld = AgentSection(
    name="3par_ld",
    parse_function=parse_3par_ld,
    parsed_section_name="3par_ld",
)


def discovery_3par_ld(section: Section) -> DiscoveryResult:
    """if data is present return one service per ld"""
    if section:
        for element in section:
            yield Service(item=element)


def check_3par_ld(item: str, section: Section) -> CheckResult:
    """check the ld state"""
    data = section.get(item)
    if not data:
        return

    message = f"LD {data.ld_id.zfill(3)}/{data.name} ({data.size_mb} MB) RAID {data.raid} \
        with status {data.state} is owned by {data.owner}"
    if data.state == "normal":
        yield Result(state=State.OK, summary=message)
    else:
        yield Result(state=State.CRIT, summary=message + "(!!)")


check_plugin_3par_ld = CheckPlugin(
    name="3par_ld",
    service_name="LD %s",
    sections=["3par_ld"],
    discovery_function=discovery_3par_ld,
    check_function=check_3par_ld,
)

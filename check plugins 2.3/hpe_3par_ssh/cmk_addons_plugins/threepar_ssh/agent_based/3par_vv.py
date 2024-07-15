#!/usr/bin/env python3
"""check for HPE 3Par vv status"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

# Example output from agent:
# <<<3par_vv>>>
# 1 .srdata                   full base ---       1 RW normal               0      0    81920    81920
# 0 admin                     full base ---       0 RW normal               0      0    10240    10240
# 3 VV_FILE_DEVWSMZ-S02090    tpvv base ---       3 RW normal             384   8704    41216   102400
# 4 VV_FILE_DEVWSMZ-S88029    tpvv base ---       4 RW normal             384   8704    16512   102400

# The names of the columns are:
#                                                                       ------Rsvd(MB)------- --(MB)--
# Id Name                      Prov Type CopyOf BsId Rd -Detailed_State-   Adm    Snp      Usr    VSize

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
class ThreeParVV:
    """one vv"""

    name: str
    prov: str
    vv_type: str
    copyof: str
    base_id: str
    read_write: str
    state: str
    rsvd_adm: str
    rsvd_snp: str
    rsvd_usr: str
    vsize: str


Section = Mapping[str, ThreeParVV]


def parse_3par_vv(string_table: StringTable) -> Section:
    """parse raw data into dict"""
    parsed: dict[str, ThreeParVV] = {}
    for line in string_table:
        if len(line) == 12 and line[0].isdigit():
            for (
                vv_id,
                name,
                prov,
                vv_type,
                copyof,
                base_id,
                read_write,
                state,
                rsvd_adm,
                rsvd_snp,
                rsvd_usr,
                vsize,
            ) in line:
                parsed.setdefault(
                    vv_id,
                    ThreeParVV(
                        name,
                        prov,
                        vv_type,
                        copyof,
                        base_id,
                        read_write,
                        state,
                        rsvd_adm,
                        rsvd_snp,
                        rsvd_usr,
                        vsize,
                    ),
                )
    return parsed


agent_section_3par_vv = AgentSection(
    name="3par_vv",
    parse_function=parse_3par_vv,
    parsed_section_name="3par_vv",
)


def discovery_3par_vv(section: Section) -> DiscoveryResult:
    """if data is present return one service per vv"""
    if section:
        for element in section:
            yield Service(item=element)


def check_3par_vv(item: str, section: Section) -> CheckResult:
    """check the vv state"""
    data = section.get(item)
    if not data:
        return

    # _reserved_space = int(data.rsvd_adm) + int(data.rsvd_snp) + int(data.rsvd_usr)
    message = f"VV {data.vv_id.zfill(3)}/{data.name} ({data.vsize} MB) has status {data.state}"
    if data.state == "normal":
        yield Result(state=State.OK, summary=message)
    else:
        yield Result(state=State.CRIT, summary=message + "(!!)")


check_plugin_3par_vv = CheckPlugin(
    name="3par_vv",
    service_name="VV %s",
    sections=["3par_vv"],
    discovery_function=discovery_3par_vv,
    check_function=check_3par_vv,
)

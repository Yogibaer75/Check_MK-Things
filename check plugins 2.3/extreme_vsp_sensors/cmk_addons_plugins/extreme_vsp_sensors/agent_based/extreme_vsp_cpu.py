#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Mapping, Optional, Tuple

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    StringTable,
    all_of,
    check_levels,
    startswith,
)
from cmk.plugins.lib.netextreme import DETECT_NETEXTREME
from pytest import param

Section = Mapping[str, float]

DETECT_VSP = all_of(
    startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1916.2.325"),
    startswith(".1.3.6.1.2.1.1.1.0", "VSP-74"),
)


def parse_extreme_vsp_cpu(string_table: StringTable) -> Optional[Section]:
    """
    >>> parse_extreme_vsp_cpu([["5"]])
    {'cpu_util': 5.0}
    """
    return {"cpu_util": float(string_table[0][0])} if string_table else None


def discovery_extreme_vsp_cpu(section: Section) -> DiscoveryResult:
    if section:
        yield Service()


def check_extreme_vsp_cpu(
    params: Mapping[str, Optional[Tuple[float, float]]],
    section: Section,
) -> CheckResult:
    if params.get("cpu_util") is None:
        levels = ("no_levels", None)
    elif not isinstance(params.get("cpu_util", (80, 90))[0], str):
        levels = ("fixed", params.get("cpu_util", (80, 90)))
    else:
        levels = params.get("cpu_util")

    yield from check_levels(
        value=section["cpu_util"],
        levels_upper=levels,
        metric_name="util",
        label="CPU utilization",
        render_func=lambda x: f"{x:.1f}%",
    )


snmp_section_extreme_vsp_cpu = SimpleSNMPSection(
    name="extreme_vsp_cpu",
    parse_function=parse_extreme_vsp_cpu,
    detect=DETECT_NETEXTREME,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.2272.1.85.10.1.1",
        oids=[
            "2",
        ],
    ),
)

check_plugin_extreme_vsp_cpu = CheckPlugin(
    name="extreme_vsp_cpu",
    service_name="CPU utilization",
    discovery_function=discovery_extreme_vsp_cpu,
    check_function=check_extreme_vsp_cpu,
    check_default_parameters={"cpu_util": None},
    check_ruleset_name="extreme_vsp_cpu",
)

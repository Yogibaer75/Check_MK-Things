#!/usr/bin/python

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from collections.abc import Mapping, MutableMapping
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    get_value_store,
    Service,
)
from cmk.plugins.hyperv_cluster.lib import parse_hyperv, Section
from cmk.plugins.lib.df import df_check_filesystem_single, FILESYSTEM_DEFAULT_PARAMS

_MB = 1024.0 * 1024.0


def _to_mb(value: str | None) -> float | None:
    return int(value) / _MB if value else None


def discover_hyperv_cluster_csv(section: Section) -> DiscoveryResult:
    for csv in section:
        yield Service(item=csv)


def check_hyperv_cluster_csv(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:
    yield from check_cluster_shared_volume(item, params, section, get_value_store())


def check_cluster_shared_volume(
    item: str,
    params: Mapping[str, Any],
    section: Section,
    value_store: MutableMapping[str, Any],
) -> CheckResult:
    if (csv := section.get(item)) is None:
        return

    yield from df_check_filesystem_single(
        value_store,
        item,
        _to_mb(csv.get("cluster.csv.size")),
        _to_mb(csv.get("cluster.csv.free_space")),
        0,
        None,
        None,
        params=params,
    )


agent_section_hyperv_cluster_csv = AgentSection(
    name="hyperv_cluster_csv",
    parse_function=parse_hyperv,
)

check_plugin_hyperv_cluster_csv = CheckPlugin(
    name="hyperv_cluster_csv",
    service_name="Hyper-V cluster CSV %s",
    discovery_function=discover_hyperv_cluster_csv,
    check_function=check_hyperv_cluster_csv,
    check_ruleset_name="filesystem",
    check_default_parameters=FILESYSTEM_DEFAULT_PARAMS,
)

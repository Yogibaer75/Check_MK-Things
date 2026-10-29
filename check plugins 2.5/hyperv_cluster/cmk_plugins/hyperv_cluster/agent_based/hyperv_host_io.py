#!/usr/bin/python

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

import time
from collections.abc import Mapping, MutableMapping
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    get_value_store,
    Result,
    Service,
    State,
)
from cmk.plugins.hyperv_cluster.lib import parse_hyperv_io, Section
from cmk.plugins.lib.diskstat import check_diskstat_dict

# agent counter name -> diskstat key
_COUNTERS = {
    "avg. disk read queue length": "read_ql",
    "avg. disk write queue length": "write_ql",
    "avg. disk sec/read": "average_read_wait",
    "avg. disk sec/write": "average_write_wait",
    "disk reads/sec": "read_ios",
    "disk writes/sec": "write_ios",
    "disk read bytes/sec": "read_throughput",
    "disk write bytes/sec": "write_throughput",
}


def discover_hyperv_host_io(
    section_hyperv_host_io_local: Section | None,
    section_hyperv_host_io_remote: Section | None,
) -> DiscoveryResult:
    for lun in {**(section_hyperv_host_io_remote or {}), **(section_hyperv_host_io_local or {})}:
        yield Service(item=lun)


def check_hyperv_host_io(
    item: str,
    params: Mapping[str, Any],
    section_hyperv_host_io_local: Section | None,
    section_hyperv_host_io_remote: Section | None,
) -> CheckResult:
    yield from check_volume_io(
        item,
        params,
        section_hyperv_host_io_local,
        section_hyperv_host_io_remote,
        get_value_store(),
        time.time(),
    )


def check_volume_io(
    item: str,
    params: Mapping[str, Any],
    local: Section | None,
    remote: Section | None,
    value_store: MutableMapping[str, Any],
    now: float,
) -> CheckResult:
    if local and (lun := local.get(item)) is not None:
        owner = "this node"
    elif remote and (lun := remote.get(item)) is not None:
        owner = "another node"
    else:
        return

    if not (
        disk := {
            key: float(lun[counter].replace(",", "."))
            for counter, key in _COUNTERS.items()
            if counter in lun
        }
    ):
        yield Result(state=State.UNKNOWN, summary="No I/O counters reported")
        return

    yield Result(state=State.OK, summary=f"Owned by {owner}")
    yield from check_diskstat_dict(
        params=params,
        disk=disk,
        value_store=value_store,
        this_time=now,
    )


agent_section_hyperv_host_io_local = AgentSection(
    name="hyperv_host_io_local",
    parse_function=parse_hyperv_io,
)

agent_section_hyperv_host_io_remote = AgentSection(
    name="hyperv_host_io_remote",
    parse_function=parse_hyperv_io,
)

check_plugin_hyperv_host_io = CheckPlugin(
    name="hyperv_host_io",
    service_name="Hyper-V cluster CSV IO %s",
    sections=["hyperv_host_io_local", "hyperv_host_io_remote"],
    discovery_function=discover_hyperv_host_io,
    check_function=check_hyperv_host_io,
    check_ruleset_name="diskstat",
    check_default_parameters={},
)

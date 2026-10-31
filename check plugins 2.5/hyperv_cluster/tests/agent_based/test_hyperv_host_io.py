#!/usr/bin/python

# License: GNU General Public License v2

from cmk.agent_based.v2 import Metric, Result, Service, State
from cmk.plugins.hyperv_cluster.agent_based.hyperv_host_io import (
    agent_section_hyperv_host_io_local,
    check_volume_io,
    discover_hyperv_host_io,
)

parse = agent_section_hyperv_host_io_local.parse_function

# Written by hyperv_host_csv_io.ps1
STRING_TABLE = [
    ["Cluster", "Disk", "1\\disk", "reads/sec", "150"],
    ["Cluster", "Disk", "1\\disk", "writes/sec", "50"],
    ["Cluster", "Disk", "1\\disk", "read", "bytes/sec", "1048576"],
    ["Cluster", "Disk", "1\\disk", "write", "bytes/sec", "524288"],
    ["Cluster", "Disk", "1\\avg.", "disk", "read", "queue", "length", "0.25"],
    ["Cluster", "Disk", "1\\avg.", "disk", "write", "queue", "length", "1"],
    ["Cluster", "Disk", "1\\avg.", "disk", "sec/read", "0.002"],
    ["Cluster", "Disk", "1\\avg.", "disk", "sec/write", "0.004"],
]

# Written by older versions of the plug-in with localized counter names
LEGACY_STRING_TABLE = [
    ["\\\\hv01\\Volume1\\lesevorgänge/s", "150,5"],
    ["\\\\hv01\\Volume1\\bytes", "gelesen/s", "1048576"],
]


def test_discovers_local_and_remote_volumes_once() -> None:
    local = parse(STRING_TABLE)
    remote = parse([["Volume2\\disk", "reads/sec", "1"], *STRING_TABLE])

    assert sorted(discover_hyperv_host_io(local, remote), key=lambda s: str(s.item)) == [
        Service(item="Cluster Disk 1"),
        Service(item="Volume2"),
    ]


def test_reports_owner_throughput_operations_latency_and_queue_lengths() -> None:
    results = list(check_volume_io("Cluster Disk 1", {}, parse(STRING_TABLE), None, {}, 0.0))

    assert results[0] == Result(state=State.OK, summary="Owned by this node")
    assert {
        Metric("disk_read_throughput", 1048576.0),
        Metric("disk_write_throughput", 524288.0),
        Metric("disk_average_read_wait", 0.002),
        Metric("disk_average_write_wait", 0.004),
        Metric("disk_read_ql", 0.25),
        Metric("disk_write_ql", 1.0),
        Metric("disk_read_ios", 150.0),
        Metric("disk_write_ios", 50.0),
    } <= set(results)
    assert any(isinstance(r, Result) and r.summary.startswith("Latency:") for r in results)


def test_latency_levels_apply() -> None:
    results = list(
        check_volume_io(
            "Cluster Disk 1",
            {"latency": ("fixed", (0.001, 0.003))},
            parse(STRING_TABLE),
            None,
            {},
            0.0,
        )
    )

    assert State.worst(*(r.state for r in results if isinstance(r, Result))) is State.CRIT


def test_volume_owned_by_another_node() -> None:
    results = list(check_volume_io("Cluster Disk 1", {}, None, parse(STRING_TABLE), {}, 0.0))

    assert results[0] == Result(state=State.OK, summary="Owned by another node")


def test_reads_localized_counters_with_decimal_comma() -> None:
    results = list(check_volume_io("Volume1", {}, parse(LEGACY_STRING_TABLE), None, {}, 0.0))

    assert [r for r in results if isinstance(r, Metric)] == [
        Metric("disk_read_throughput", 1048576.0),
        Metric("disk_read_ios", 150.5),
    ]


def test_missing_counters_do_not_crash() -> None:
    results = list(
        check_volume_io("Volume2", {}, parse([["Volume2\\disk", "reads/sec", "7"]]), None, {}, 0.0)
    )

    assert Metric("disk_read_ios", 7.0) in results


def test_volume_without_counters_is_unknown() -> None:
    results = list(
        check_volume_io("Volume2", {}, parse([["Volume2\\unknown", "counter", "7"]]), None, {}, 0.0)
    )

    assert results == [Result(state=State.UNKNOWN, summary="No I/O counters reported")]


def test_vanished_volume_yields_no_result() -> None:
    assert not list(check_volume_io("Volume9", {}, parse(STRING_TABLE), None, {}, 0.0))

#!/usr/bin/python

# License: GNU General Public License v2

import time
from collections.abc import Iterable

import pytest

from cmk.agent_based.v2 import Metric, Result, Service, State
from cmk.plugins.hyperv_cluster.agent_based import hyperv_cluster_csv
from cmk.plugins.hyperv_cluster.agent_based.hyperv_cluster_csv import (
    check_cluster_shared_volume,
    cluster_check_hyperv_cluster_csv,
    discover_hyperv_cluster_csv,
)
from cmk.plugins.hyperv_cluster.lib import parse_hyperv, Section
from cmk.plugins.lib.df import FILESYSTEM_DEFAULT_PARAMS

_GIB = 1024**3

STRING_TABLE = [
    ["cluster.number_of_csv", "1"],
    ["cluster.csv.name", "Cluster", "Disk", "2"],
    ["cluster.csv.owner", "HV01"],
    ["cluster.csv.volume", "C:\\ClusterStorage\\Volume1"],
    ["cluster.csv.size", str(100 * _GIB)],
    ["cluster.csv.free_space", str(50 * _GIB)],
    ["cluster.csv.used_space", str(50 * _GIB)],
]


def _section(size: int, free: int | None) -> Section:
    lines = [
        ["cluster.number_of_csv", "1"],
        ["cluster.csv.name", "Cluster", "Disk", "2"],
        ["cluster.csv.size", str(size)],
    ]
    if free is not None:
        lines.append(["cluster.csv.free_space", str(free)])
    return parse_hyperv(lines)


def _value_store(used_mb: float) -> dict[str, object]:
    # The trend computation needs a previous value
    return {"Cluster Disk 2.delta": (time.time() - 60, used_mb)}


def _worst_state(results: Iterable[object]) -> State:
    return State.worst(*(r.state for r in results if isinstance(r, Result)))


def test_discovers_every_cluster_shared_volume() -> None:
    section = parse_hyperv(STRING_TABLE)

    assert list(discover_hyperv_cluster_csv(section)) == [Service(item="Cluster Disk 2")]


def test_half_full_volume_is_ok() -> None:
    section = parse_hyperv(STRING_TABLE)

    results = list(
        check_cluster_shared_volume(
            "Cluster Disk 2", FILESYSTEM_DEFAULT_PARAMS, section, _value_store(50 * 1024)
        )
    )

    assert (
        Metric("fs_used", 50 * 1024, levels=(80 * 1024, 90 * 1024), boundaries=(0, 100 * 1024))
        in results
    )
    assert _worst_state(results) is State.OK


def test_full_volume_exceeds_default_levels() -> None:
    results = list(
        check_cluster_shared_volume(
            "Cluster Disk 2",
            FILESYSTEM_DEFAULT_PARAMS,
            _section(100 * _GIB, 5 * _GIB),
            _value_store(95 * 1024),
        )
    )

    assert _worst_state(results) is State.CRIT


def test_configured_levels_apply() -> None:
    results = list(
        check_cluster_shared_volume(
            "Cluster Disk 2",
            {**FILESYSTEM_DEFAULT_PARAMS, "levels": (40.0, 60.0)},
            _section(100 * _GIB, 50 * _GIB),
            _value_store(50 * 1024),
        )
    )

    assert _worst_state(results) is State.WARN


def test_missing_free_space_is_not_reported_as_full() -> None:
    results = list(
        check_cluster_shared_volume(
            "Cluster Disk 2", FILESYSTEM_DEFAULT_PARAMS, _section(100 * _GIB, None), {}
        )
    )

    assert _worst_state(results) is not State.CRIT
    assert not any(isinstance(r, Metric) and r.name == "fs_used" for r in results)


def test_vanished_volume_yields_no_result() -> None:
    section = parse_hyperv(STRING_TABLE)

    assert not list(
        check_cluster_shared_volume("Cluster Disk 3", FILESYSTEM_DEFAULT_PARAMS, section, {})
    )


def test_cluster_uses_the_report_of_the_first_node(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(hyperv_cluster_csv, "get_value_store", lambda: _value_store(95 * 1024))

    results = list(
        cluster_check_hyperv_cluster_csv(
            "Cluster Disk 2",
            FILESYSTEM_DEFAULT_PARAMS,
            {
                "HV02": _section(100 * _GIB, 50 * _GIB),
                "HV01": _section(100 * _GIB, 5 * _GIB),
                "HV03": None,
            },
        )
    )

    assert _worst_state(results) is State.CRIT


def test_cluster_without_reports_yields_no_result(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(hyperv_cluster_csv, "get_value_store", dict)

    assert not list(
        cluster_check_hyperv_cluster_csv(
            "Cluster Disk 2", FILESYSTEM_DEFAULT_PARAMS, {"HV01": None, "HV02": None}
        )
    )

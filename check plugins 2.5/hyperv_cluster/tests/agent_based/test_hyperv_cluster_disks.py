#!/usr/bin/python

# License: GNU General Public License v2

import pytest

from cmk.agent_based.v2 import Result, Service, State
from cmk.plugins.hyperv_cluster.agent_based.hyperv_cluster_disks import (
    check_hyperv_cluster_disks,
    cluster_check_hyperv_cluster_disks,
    discover_hyperv_cluster_disks,
)
from cmk.plugins.hyperv_cluster.lib import parse_hyperv, Section


def _section(state: str = "Online") -> Section:
    return parse_hyperv(
        [
            ["cluster.number_of_disks", "2"],
            ["cluster.disk.name", "Cluster", "Disk", "1"],
            ["cluster.disk.owner_group", "Cluster", "Group"],
            ["cluster.disk.owner_node", "HV01"],
            ["cluster.disk.state", "Online"],
            ["cluster.disk.name", "Cluster", "Disk", "2"],
            ["cluster.disk.owner_group", "Available", "Storage"],
            ["cluster.disk.owner_node", "HV02"],
            ["cluster.disk.state", state],
        ]
    )


def test_discovers_every_disk() -> None:
    assert list(discover_hyperv_cluster_disks(_section())) == [
        Service(item="Cluster Disk 1"),
        Service(item="Cluster Disk 2"),
    ]


def test_online_disk_is_ok() -> None:
    assert list(check_hyperv_cluster_disks("Cluster Disk 1", _section())) == [
        Result(state=State.OK, summary="State: Online"),
        Result(state=State.OK, summary="Owner: HV01"),
        Result(state=State.OK, summary="Group: Cluster Group"),
    ]


@pytest.mark.parametrize(
    "disk_state, expected",
    [
        pytest.param("Initializing", State.WARN, id="initializing"),
        pytest.param("Pending", State.WARN, id="pending"),
        pytest.param("OnlinePending", State.WARN, id="online pending"),
        pytest.param("OfflinePending", State.WARN, id="offline pending"),
        pytest.param("Offline", State.CRIT, id="offline"),
        pytest.param("Failed", State.CRIT, id="failed"),
        pytest.param("Unknown", State.UNKNOWN, id="unknown"),
    ],
)
def test_disk_state_sets_service_state(disk_state: str, expected: State) -> None:
    results = list(check_hyperv_cluster_disks("Cluster Disk 2", _section(disk_state)))

    assert results[0] == Result(state=expected, summary=f"State: {disk_state}")


def test_missing_values_are_left_out() -> None:
    section = parse_hyperv(
        [
            ["cluster.number_of_disks", "1"],
            ["cluster.disk.name", "Cluster", "Disk", "1"],
            ["cluster.disk.owner_node"],
        ]
    )

    assert list(check_hyperv_cluster_disks("Cluster Disk 1", section)) == [
        Result(state=State.UNKNOWN, summary="State: not reported"),
    ]


def test_vanished_disk_yields_no_result() -> None:
    assert not list(check_hyperv_cluster_disks("Cluster Disk 3", _section()))


def test_cluster_uses_the_report_of_the_first_node() -> None:
    results = list(
        cluster_check_hyperv_cluster_disks(
            "Cluster Disk 2", {"HV02": _section("Online"), "HV01": _section("Failed"), "HV03": None}
        )
    )

    assert results[0] == Result(state=State.CRIT, summary="State: Failed")

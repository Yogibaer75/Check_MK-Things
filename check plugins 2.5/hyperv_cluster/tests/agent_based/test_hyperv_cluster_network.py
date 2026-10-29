#!/usr/bin/python

# License: GNU General Public License v2

import pytest

from cmk.agent_based.v2 import Result, Service, State
from cmk.plugins.hyperv_cluster.agent_based.hyperv_cluster_network import (
    check_hyperv_cluster_network,
    cluster_check_hyperv_cluster_network,
    discover_hyperv_cluster_network,
)
from cmk.plugins.hyperv_cluster.lib import parse_hyperv, Section


def _section(state: str = "Up") -> Section:
    return parse_hyperv(
        [
            ["cluster.number_of_networks", "2"],
            ["cluster.network.name", "Cluster", "Network", "1"],
            ["cluster.network.role", "ClusterAndClient"],
            ["cluster.network.state", "Up"],
            ["cluster.network.ip", "10.0.0.0"],
            ["cluster.network.netmask", "255.255.255.0"],
            ["cluster.network.name", "Cluster", "Network", "2"],
            ["cluster.network.role", "Cluster"],
            ["cluster.network.state", state],
            ["cluster.network.ip", "10.0.1.0"],
        ]
    )


def test_discovers_every_network() -> None:
    assert list(discover_hyperv_cluster_network(_section())) == [
        Service(item="Cluster Network 1"),
        Service(item="Cluster Network 2"),
    ]


def test_up_network_is_ok() -> None:
    assert list(check_hyperv_cluster_network("Cluster Network 1", _section())) == [
        Result(state=State.OK, summary="State: Up"),
        Result(state=State.OK, summary="Address: 10.0.0.0"),
        Result(state=State.OK, summary="Role: ClusterAndClient"),
    ]


@pytest.mark.parametrize(
    "network_state, expected",
    [
        pytest.param("Partitioned", State.WARN, id="partitioned"),
        pytest.param("Down", State.CRIT, id="down"),
        pytest.param("Unavailable", State.CRIT, id="unavailable"),
        pytest.param("Unknown", State.UNKNOWN, id="unknown"),
    ],
)
def test_network_state_sets_service_state(network_state: str, expected: State) -> None:
    results = list(check_hyperv_cluster_network("Cluster Network 2", _section(network_state)))

    assert results[0] == Result(state=expected, summary=f"State: {network_state}")


def test_missing_values_are_left_out() -> None:
    section = parse_hyperv(
        [
            ["cluster.number_of_networks", "1"],
            ["cluster.network.name", "Cluster", "Network", "1"],
            ["cluster.network.role"],
        ]
    )

    assert list(check_hyperv_cluster_network("Cluster Network 1", section)) == [
        Result(state=State.UNKNOWN, summary="State: not reported"),
    ]


def test_vanished_network_yields_no_result() -> None:
    assert not list(check_hyperv_cluster_network("Cluster Network 3", _section()))


def test_cluster_uses_the_report_of_the_first_node() -> None:
    results = list(
        cluster_check_hyperv_cluster_network(
            "Cluster Network 2", {"HV02": _section("Up"), "HV01": _section("Down"), "HV03": None}
        )
    )

    assert results[0] == Result(state=State.CRIT, summary="State: Down")

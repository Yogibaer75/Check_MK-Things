#!/usr/bin/python

# License: GNU General Public License v2

import pytest

from cmk.agent_based.v2 import Result, Service, State
from cmk.plugins.hyperv_cluster.agent_based.hyperv_cluster_nodes import (
    check_hyperv_cluster_nodes,
    discover_hyperv_cluster_nodes,
)
from cmk.plugins.hyperv_cluster.lib import parse_hyperv, Section


def _section(state: str = "Up", info: str = "Normal") -> Section:
    return parse_hyperv(
        [
            ["cluster.number_of_nodes", "2"],
            ["cluster.node.name", "HV01"],
            ["cluster.node.id", "1"],
            ["cluster.node.state", "Up"],
            ["cluster.node.info", "Normal"],
            ["cluster.node.weight", "1"],
            ["cluster.node_vendor.manufacturer", "HPE"],
            ["cluster.node.name", "HV02"],
            ["cluster.node.id", "2"],
            ["cluster.node.state", *state.split()],
            ["cluster.node.info", *info.split()],
            ["cluster.node.weight", "1"],
        ]
    )


def test_discovers_every_node() -> None:
    assert list(discover_hyperv_cluster_nodes(_section())) == [
        Service(item="HV01"),
        Service(item="HV02"),
    ]


def test_up_node_is_ok() -> None:
    assert list(check_hyperv_cluster_nodes("HV01", _section())) == [
        Result(state=State.OK, summary="State: Up"),
        Result(state=State.OK, summary="ID: 1"),
        Result(state=State.OK, summary="Weight: 1"),
        Result(state=State.OK, notice="Status information: Normal"),
    ]


@pytest.mark.parametrize(
    "node_state, expected",
    [
        pytest.param("Up", State.OK, id="up"),
        pytest.param("Paused", State.WARN, id="paused"),
        pytest.param("Joining", State.WARN, id="joining"),
        pytest.param("Down", State.CRIT, id="down"),
        pytest.param("Unknown", State.UNKNOWN, id="unknown"),
    ],
)
def test_node_state_sets_service_state(node_state: str, expected: State) -> None:
    results = list(check_hyperv_cluster_nodes("HV02", _section(state=node_state)))

    assert results[0] == Result(state=expected, summary=f"State: {node_state}")


@pytest.mark.parametrize(
    "info, expected",
    [
        pytest.param("Isolated", State.WARN, id="isolated"),
        pytest.param("Quarantined", State.CRIT, id="quarantined"),
    ],
)
def test_isolated_or_quarantined_node(info: str, expected: State) -> None:
    results = list(check_hyperv_cluster_nodes("HV02", _section(info=info)))

    assert results[-1] == Result(state=expected, summary=f"Status information: {info}")


def test_missing_values_are_left_out() -> None:
    section = parse_hyperv(
        [
            ["cluster.number_of_nodes", "1"],
            ["cluster.node.name", "HV01"],
            ["cluster.node.id"],
            ["cluster.node.info"],
        ]
    )

    assert list(check_hyperv_cluster_nodes("HV01", section)) == [
        Result(state=State.UNKNOWN, summary="State: not reported"),
    ]


def test_vanished_node_yields_no_result() -> None:
    assert not list(check_hyperv_cluster_nodes("HV03", _section()))

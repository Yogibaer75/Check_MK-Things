#!/usr/bin/python

# License: GNU General Public License v2

import pytest

from cmk.agent_based.v2 import Result, Service, State
from cmk.plugins.hyperv_cluster.agent_based.hyperv_cluster_roles import (
    check_hyperv_cluster_roles,
    cluster_check_hyperv_cluster_roles,
    discover_hyperv_cluster_roles,
    RolesParams,
)
from cmk.plugins.hyperv_cluster.lib import parse_hyperv, Section

ONLINE: RolesParams = {"expected_state": "active"}
OFFLINE: RolesParams = {"expected_state": "inactive"}
IGNORE: RolesParams = {"expected_state": "ignore"}


def _section(state: str, owner: str = "HV01") -> Section:
    return parse_hyperv(
        [
            ["cluster.number_of_vms", "1"],
            ["cluster.vm.name", "SRV-APP01"],
            ["cluster.vm.state", state],
            ["cluster.vm.owner", *owner.split()],
        ]
    )


def test_discovers_every_clustered_vm() -> None:
    assert list(discover_hyperv_cluster_roles(_section("Online"))) == [Service(item="SRV-APP01")]


def test_online_vm_shows_running_node() -> None:
    assert list(check_hyperv_cluster_roles("SRV-APP01", ONLINE, _section("Online"))) == [
        Result(state=State.OK, summary="Power state: Online"),
        Result(state=State.OK, summary="Running on: HV01"),
    ]


def test_partially_online_vm_shows_running_node() -> None:
    assert list(check_hyperv_cluster_roles("SRV-APP01", ONLINE, _section("PartialOnline"))) == [
        Result(state=State.WARN, summary="Power state: PartialOnline (expected: Online)"),
        Result(state=State.OK, summary="Running on: HV01"),
    ]


def test_offline_vm_shows_defining_node() -> None:
    assert list(check_hyperv_cluster_roles("SRV-APP01", OFFLINE, _section("Offline"))) == [
        Result(state=State.OK, summary="Power state: Offline"),
        Result(state=State.OK, summary="Defined on: HV01"),
    ]


def test_vm_without_owner_is_reported_as_unassigned() -> None:
    results = list(check_hyperv_cluster_roles("SRV-APP01", OFFLINE, _section("Offline", owner="")))

    assert results[1] == Result(state=State.OK, summary="Not assigned to a node")


@pytest.mark.parametrize(
    "vm_state, online, offline, ignore",
    [
        pytest.param("Online", State.OK, State.WARN, State.OK, id="online"),
        pytest.param("Offline", State.WARN, State.OK, State.OK, id="offline"),
        pytest.param("PartialOnline", State.WARN, State.WARN, State.OK, id="partially online"),
        pytest.param("Pending", State.WARN, State.WARN, State.OK, id="pending"),
        pytest.param("Failed", State.CRIT, State.CRIT, State.CRIT, id="failed"),
        pytest.param("Unknown", State.UNKNOWN, State.UNKNOWN, State.OK, id="unknown"),
    ],
)
def test_power_state_against_expected_state(
    vm_state: str, online: State, offline: State, ignore: State
) -> None:
    section = _section(vm_state)

    assert [_power_state_result(params, section).state for params in (ONLINE, OFFLINE, IGNORE)] == [
        online,
        offline,
        ignore,
    ]


def _power_state_result(params: RolesParams, section: Section) -> Result:
    result = next(iter(check_hyperv_cluster_roles("SRV-APP01", params, section)))
    assert isinstance(result, Result)
    return result


def test_unexpected_state_names_the_expected_one() -> None:
    results = list(check_hyperv_cluster_roles("SRV-APP01", OFFLINE, _section("Online")))

    assert results[0] == Result(state=State.WARN, summary="Power state: Online (expected: Offline)")


def test_cluster_shows_the_most_favourable_node_report() -> None:
    results = list(
        cluster_check_hyperv_cluster_roles(
            "SRV-APP01",
            ONLINE,
            {"HV01": _section("Offline"), "HV02": _section("Online", owner="HV02"), "HV03": None},
        )
    )

    assert results == [
        Result(state=State.OK, summary="Power state: Online"),
        Result(state=State.OK, summary="Running on: HV02"),
    ]


def test_cluster_with_failed_vm_on_all_nodes_is_crit() -> None:
    results = list(
        cluster_check_hyperv_cluster_roles(
            "SRV-APP01", IGNORE, {"HV01": _section("Failed"), "HV02": _section("Failed")}
        )
    )

    assert results[0] == Result(state=State.CRIT, summary="Power state: Failed")


def test_cluster_yields_no_result_for_unknown_vm() -> None:
    assert not list(
        cluster_check_hyperv_cluster_roles(
            "SRV-DB01", ONLINE, {"HV01": _section("Online"), "HV02": None}
        )
    )

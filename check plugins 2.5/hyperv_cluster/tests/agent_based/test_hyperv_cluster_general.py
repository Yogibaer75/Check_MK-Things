#!/usr/bin/python

# License: GNU General Public License v2

from cmk.agent_based.v2 import Result, Service, State
from cmk.plugins.hyperv_cluster.agent_based.hyperv_cluster_general import (
    check_hyperv_cluster_general,
    discover_hyperv_cluster_general,
)
from cmk.plugins.hyperv_cluster.lib import hyperv_vm_convert as parse

STRING_TABLE = [
    ["cluster.name", "HVCLUSTER01"],
    ["cluster.ip", "10.0.0.10"],
    ["cluster.subnet", "255.255.255.0"],
    ["quorum.resourcename", "Cluster", "Disk", "Witness"],
    ["quorum.type", "NodeAndDiskMajority"],
]


def test_discovers_the_cluster() -> None:
    assert list(discover_hyperv_cluster_general(parse(STRING_TABLE))) == [Service()]


def test_no_service_without_cluster_name() -> None:
    assert not list(discover_hyperv_cluster_general(parse([["quorum.type", "NodeMajority"]])))


def test_shows_name_ip_and_quorum() -> None:
    assert list(check_hyperv_cluster_general(parse(STRING_TABLE))) == [
        Result(state=State.OK, summary="Name: HVCLUSTER01"),
        Result(state=State.OK, summary="IP: 10.0.0.10"),
        Result(state=State.OK, summary="Quorum: Cluster Disk Witness (NodeAndDiskMajority)"),
    ]


def test_quorum_without_resource_and_missing_ip() -> None:
    section = parse(
        [
            ["cluster.name", "HVCLUSTER01"],
            ["cluster.ip"],
            ["quorum.resourcename"],
            ["quorum.type", "NodeMajority"],
        ]
    )

    assert list(check_hyperv_cluster_general(section)) == [
        Result(state=State.OK, summary="Name: HVCLUSTER01"),
        Result(state=State.OK, summary="Quorum: NodeMajority"),
    ]

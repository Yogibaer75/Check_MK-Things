#!/usr/bin/python

# License: GNU General Public License v2

import pytest

from cmk.plugins.hyperv_cluster.rulesets.hyperv_cluster_roles import rule_spec_hyperv_cluster_roles


@pytest.mark.parametrize(
    "value, expected",
    [
        pytest.param(
            {"default_status": "inactive", "match_services": [("SRV-APP01", "active")]},
            {"expected_state": "inactive"},
            id="old parameters with per-VM states as tuples",
        ),
        pytest.param(
            {
                "default_status": "ignore",
                "match_services": [{"service_name": "SRV-APP01", "state": "active"}],
            },
            {"expected_state": "ignore"},
            id="old parameters with per-VM states as dictionaries",
        ),
        pytest.param(
            {"match_services": []},
            {"expected_state": "active"},
            id="old parameters without default state",
        ),
        pytest.param(
            {},
            {"expected_state": "active"},
            id="empty old parameters",
        ),
        pytest.param(
            {"expected_state": "ignore"},
            {"expected_state": "ignore"},
            id="current parameters",
        ),
    ],
)
def test_migrates_old_parameters(value: object, expected: dict[str, str]) -> None:
    form = rule_spec_hyperv_cluster_roles.parameter_form()

    assert form.migrate is not None
    assert form.migrate(value) == expected


def test_rejects_invalid_parameters() -> None:
    form = rule_spec_hyperv_cluster_roles.parameter_form()

    assert form.migrate is not None
    with pytest.raises(TypeError):
        form.migrate("active")

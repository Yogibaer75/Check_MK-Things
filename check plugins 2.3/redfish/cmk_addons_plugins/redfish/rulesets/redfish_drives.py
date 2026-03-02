#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""rule for discovery of drive items"""

from cmk.rulesets.v1 import form_specs, Help, rule_specs, Title  # type: ignore[import]


def _form_discovery_redfish_drives() -> form_specs.Dictionary:
    return form_specs.Dictionary(
        title=Title("Redfish physical drive discovery"),
        elements={
            "item": form_specs.DictElement(
                parameter_form=form_specs.SingleChoice(
                    title=Title("Discovery settings for physical drives"),
                    help_text=Help("Specify if drive item should be the current version or "
                                   "item should be build from controller and drive id."),
                    elements=[
                        form_specs.SingleChoiceElement(name="classic", title=Title("Classic")),
                        form_specs.SingleChoiceElement(name="ctrlid", title=Title("Controller ID")),
                    ],
                ),
            ),
        },
    )


rule_spec_discovery_redfish_drives = rule_specs.DiscoveryParameters(
    title=Title("Redfish Physical Drive discovery"),
    topic=rule_specs.Topic.SERVER_HARDWARE,
    name="discovery_redfish_drives",
    parameter_form=_form_discovery_redfish_drives,
)

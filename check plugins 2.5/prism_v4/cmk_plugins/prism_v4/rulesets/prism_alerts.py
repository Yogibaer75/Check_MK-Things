#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.rulesets.v1 import Help, Label, Title, form_specs, rule_specs


def _parameter_form_prism_alerts_v4() -> form_specs.Dictionary:
    return form_specs.Dictionary(
        elements={
            "prism_central_only": form_specs.DictElement(
                parameter_form=form_specs.BooleanChoice(
                    title=Title("Consider alerts for Prism Central only"),
                    label=Label("Activate (off: consider all alerts)"),
                    prefill=form_specs.DefaultValue(False),
                ),
            ),
            "ignore_acknowledged": form_specs.DictElement(
                parameter_form=form_specs.BooleanChoice(
                    title=Title("Ignore acknowledged alerts"),
                    label=Label("Acknowledged alerts don't count and don't change the state"),
                    help_text=Help(
                        "Alerts which were acknowledged in Prism are still listed by the "
                        "API until they are resolved. With this option they are ignored."
                    ),
                    prefill=form_specs.DefaultValue(True),
                ),
            ),
        },
        title=Title("Nutanix Prism alerts"),
    )


rule_spec_prism_alerts_v4 = rule_specs.CheckParameters(
    name="prism_alerts_v4",
    topic=rule_specs.Topic.VIRTUALIZATION,
    parameter_form=_parameter_form_prism_alerts_v4,
    title=Title("Nutanix Prism Alerts (API v4)"),
    condition=rule_specs.HostCondition(),
)

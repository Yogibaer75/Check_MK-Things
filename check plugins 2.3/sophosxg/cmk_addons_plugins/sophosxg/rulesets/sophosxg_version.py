#!/usr/bin/env python3
"""Ruleset definition for SophosXG version check"""

# (c) Matthias Binder 'hds@kpc.de' - K&P Computer Service- und Vertriebs-GmbH
# (c) Andreas Doehler 'andreas.doehler@bechtle.com'
# License: GNU General Public License v2

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    String,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    HostCondition,
    LengthInRange,
    Topic,
)


def _parameter_valuespec_sophosxg_version():
    return Dictionary(
        elements={
            "firmware_check": DictElement(
                parameter_form=String(
                    title=Title("Expected Firmware version"),
                    help_text=Help(
                        "Check if the Sophos XG firmware version is as expected."
                    ),
                    custom_validate=(LengthInRange(min_value=1),),
                    prefill=DefaultValue("unspecified"),
                ),
            ),
        }
    )


rule_spec_sophosxg_version = CheckParameters(
    name="sophosxg_version",
    title=Title("Sophos XG Firmware"),
    topic=Topic.NETWORKING,
    condition=HostCondition(),
    parameter_form=_parameter_valuespec_sophosxg_version,
)

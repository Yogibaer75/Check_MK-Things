#!/usr/bin/env python3
"""Redfish Storage Controller Ruleset"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DictElement,
    Dictionary,
    SingleChoice,
    SingleChoiceElement,
    String,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    Topic,
    HostAndItemCondition,
    LengthInRange,
)


def _parameter_valuespec_redfish_storage() -> Dictionary:
    return Dictionary(
        elements={
            "check_type": DictElement(
                parameter_form=SingleChoice(
                    title=Title("Check Type for Storage Controller"),
                    elements=[
                        SingleChoiceElement(
                            name="full",
                            title=Title("Full controller status with sub systems"),
                        ),
                        SingleChoiceElement(
                            name="rollup",
                            title=Title("Rollup check only"),
                        ),
                    ],
                )
            ),
        },
    )


rule_spec_redfish_storage = CheckParameters(
    name="redfish_storage",
    title=Title("Redfish Storage Controller"),
    topic=Topic.SERVER_HARDWARE,
    condition=HostAndItemCondition(
        item_title=Title("Controller ID"),
        item_form=String(custom_validate=(LengthInRange(min_value=1),)),
    ),
    parameter_form=_parameter_valuespec_redfish_storage,
)

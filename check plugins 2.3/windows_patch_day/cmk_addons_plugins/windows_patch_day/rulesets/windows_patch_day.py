#!/usr/bin/env python3
"""Windows last update ruleset"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DictElement,
    Dictionary,
    InputHint,
    Integer,
    LevelDirection,
    migrate_to_integer_simple_levels,
    SimpleLevels,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, Topic, HostCondition


def _parameter_valuespec_windows_patch_day() -> Dictionary:
    return Dictionary(
        elements={
            "levels": DictElement(
                parameter_form=SimpleLevels[int](
                    title=Title("Days since update"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(),
                    migrate=migrate_to_integer_simple_levels,
                    prefill_fixed_levels=InputHint(value=(15, 30)),
                )
            ),
        },
    )


rule_spec_windows_patch_day = CheckParameters(
    name="windows_patch_day",
    title=Title("Windows Patch Day"),
    topic=Topic.OPERATING_SYSTEM,
    condition=HostCondition(),
    parameter_form=_parameter_valuespec_windows_patch_day,
)

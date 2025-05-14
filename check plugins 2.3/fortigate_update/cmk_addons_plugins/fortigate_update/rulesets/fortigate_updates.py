#!/usr/bin/env python3
"""Ruleset definition for Fortigate update check"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DictElement,
    Dictionary,
    InputHint,
    Integer,
    LevelDirection,
    SimpleLevels,
    String,
    migrate_to_integer_simple_levels,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    HostAndItemCondition,
    LengthInRange,
    Topic,
)


def _parameter_valuespec_fortigate_update() -> Dictionary:
    return Dictionary(
        elements={
            "levels": DictElement(
                parameter_form=SimpleLevels[int](
                    title=Title("Days since last update check"),
                    help_text=Help("This rule sets the days since the last time the system checked for updates."),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(),
                    migrate=migrate_to_integer_simple_levels,
                    prefill_fixed_levels=InputHint(value=(30, 90)),
                ),
            ),
        }
    )


rule_spec_fortigate_update = CheckParameters(
    name="fortigate_update",
    title=Title("Fortigate Update"),
    topic=Topic.NETWORKING,
    condition=HostAndItemCondition(
        item_title=Title("Update Name"),
        item_form=String(custom_validate=(LengthInRange(min_value=1),)),
    ),
    parameter_form=_parameter_valuespec_fortigate_update,
)

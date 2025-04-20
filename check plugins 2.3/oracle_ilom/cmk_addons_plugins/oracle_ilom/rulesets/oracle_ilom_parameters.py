#!/usr/bin/env python3
"""Oracle ILOM sensor parameters"""
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Float,
    InputHint,
    LevelDirection,
    SimpleLevels,
    SingleChoice,
    SingleChoiceElement,
    String,
    migrate_to_float_simple_levels,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    HostAndItemCondition,
    LengthInRange,
    Topic,
)


def _parameter_valuespec_ilom_sensor() -> Dictionary:
    return Dictionary(
        elements={
            "levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Upper Sensor Levels"),
                    form_spec_template=Float(),
                    prefill_fixed_levels=InputHint((20.0, 30.0)),
                    migrate=migrate_to_float_simple_levels,
                    level_direction=LevelDirection.UPPER,
                ),
            ),
            "levels_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Lower Sensor Levels"),
                    form_spec_template=Float(),
                    prefill_fixed_levels=InputHint((5.0, 1.0)),
                    migrate=migrate_to_float_simple_levels,
                    level_direction=LevelDirection.LOWER,
                ),
            ),
            "device_levels_handling": DictElement(
                parameter_form=SingleChoice(
                    title=Title("Interpretation of the device's own status"),
                    elements=[
                        SingleChoiceElement(
                            name="usr",
                            title=Title("Ignore device's own levels"),
                        ),
                        SingleChoiceElement(
                            name="dev",
                            title=Title("Only use device's levels, ignore yours"),
                        ),
                        SingleChoiceElement(
                            name="devdefault",
                            title=Title("Use device's levels if present, otherwise yours"),
                        ),
                        SingleChoiceElement(
                            name="usrdefault",
                            title=Title("Use your own levels if present, otherwise the device's"),
                        ),
                    ],
                    prefill=DefaultValue("usrdefault")
                ),
            ),
        },
    )


rule_spec_ilom_sensor = CheckParameters(
    name="ilom_sensor",
    title=Title("Oracle ILOM Sensor"),
    topic=Topic.ENVIRONMENTAL,
    condition=HostAndItemCondition(
        item_title=Title("Sensor ID"),
        item_form=String(custom_validate=(LengthInRange(min_value=1),),)
    ),
    parameter_form=_parameter_valuespec_ilom_sensor,
)

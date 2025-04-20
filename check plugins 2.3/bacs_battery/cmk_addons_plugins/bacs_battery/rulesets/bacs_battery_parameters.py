#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
"""parameters for BACS battery check"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DictElement,
    Dictionary,
    Float,
    InputHint,
    LevelDirection,
    SimpleLevels,
    String,
    migrate_to_float_simple_levels,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    Help,
    HostAndItemCondition,
    LengthInRange,
    Topic,
)


def _parameter_valuespec_bacs_battery():
    return Dictionary(
        title=Title("Voltage Sensor"),
        elements={
            "voltage": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Upper Levels for Voltage"),
                    help_text=Help(
                        "The voltage of the battery. The value is in Volts.",
                    ),
                    form_spec_template=Float(unit_symbol="V"),
                    migrate=migrate_to_float_simple_levels,
                    prefill_fixed_levels=InputHint((14.00, 15.00)),
                    level_direction=LevelDirection.UPPER,
                ),
            ),
            "voltage_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Lower Levels for Voltage"),
                    help_text=Help(
                        "The voltage of the battery. The value is in Volts.",
                    ),
                    form_spec_template=Float(unit_symbol="V"),
                    migrate=migrate_to_float_simple_levels,
                    prefill_fixed_levels=InputHint((10.00, 9.00)),
                    level_direction=LevelDirection.LOWER,
                ),
            ),
            "temp": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Upper Levels for Temperature"),
                    help_text=Help(
                        "The temperature of the battery. The value is in Celsius.",
                    ),
                    form_spec_template=Float(unit_symbol="°C"),
                    migrate=migrate_to_float_simple_levels,
                    prefill_fixed_levels=InputHint((40.00, 50.00)),
                    level_direction=LevelDirection.UPPER,
                ),
            ),
            "temp_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Lower Levels for Temperature"),
                    help_text=Help(
                        "The temperature of the battery. The value is in Celsius.",
                    ),
                    form_spec_template=Float(unit_symbol="°C"),
                    migrate=migrate_to_float_simple_levels,
                    prefill_fixed_levels=InputHint((10.00, 5.00)),
                    level_direction=LevelDirection.LOWER,
                ),
            ),
            "resistance": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Levels for inside Resistance"),
                    help_text=Help(
                        "The resistance of the battery. The value is in mOhm.",
                    ),
                    form_spec_template=Float(unit_symbol="mOhm"),
                    migrate=migrate_to_float_simple_levels,
                    prefill_fixed_levels=InputHint((15.00, 18.00)),
                    level_direction=LevelDirection.UPPER,
                ),
            ),
        }
    )


rule_spec_bacs = CheckParameters(
    name="bacs",
    title=Title("BACS Battery"),
    topic=Topic.ENVIRONMENTAL,
    condition=HostAndItemCondition(
        item_title=Title("Battery Index"),
        item_form=String(custom_validate=(LengthInRange(min_value=1),),),
    ),
    parameter_form=_parameter_valuespec_bacs_battery,
)

#!/usr/bin/env python3
"""Ruleset definition for SophosXG license check"""

# (c) Matthias Binder 'hds@kpc.de' - K&P Computer Service- und Vertriebs-GmbH
# (c) Andreas Doehler 'andreas.doehler@bechtle.com'
# License: GNU General Public License v2

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    InputHint,
    Integer,
    LevelDirection,
    SimpleLevels,
    SingleChoice,
    SingleChoiceElement,
    String,
    migrate_to_integer_simple_levels,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    HostAndItemCondition,
    LengthInRange,
    Topic,
)


def _parameter_valuespec_sophosxg_lic():
    return Dictionary(
        elements={
            "levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("License Days left"),
                    help_text=Help("Days left until the license expires."),
                    migrate=migrate_to_integer_simple_levels,
                    form_spec_template=Integer(unit_symbol="days"),
                    level_direction=LevelDirection.LOWER,
                    prefill_fixed_levels=InputHint((40, 30)),
                ),
            ),
            "state": DictElement(
                parameter_form=SingleChoice(
                    title=Title("Wanted License State"),
                    elements=[
                        SingleChoiceElement(
                            name="none",
                            title=Title("None"),
                        ),
                        SingleChoiceElement(
                            name="evaluating",
                            title=Title("Evaluating"),
                        ),
                        SingleChoiceElement(
                            name="not_subscribed",
                            title=Title("Not Subscribed"),
                        ),
                        SingleChoiceElement(
                            name="subscribed",
                            title=Title("Subscribed"),
                        ),
                        SingleChoiceElement(
                            name="expired",
                            title=Title("Expired"),
                        ),
                        SingleChoiceElement(
                            name="deactivated",
                            title=Title("Deactivated"),
                        ),
                        SingleChoiceElement(
                            name="ignored",
                            title=Title("No preference selected / ignored"),
                        ),
                    ],
                    prefill=DefaultValue("subscribed"),
                ),
            ),
        }
    )


rule_spec_sophosxg_lic = CheckParameters(
    name="sophosxg_lic",
    title=Title("Sophos XG State for Licenses & Runtime"),
    topic=Topic.NETWORKING,
    condition=HostAndItemCondition(
        item_title=Title("License"),
        item_form=String(custom_validate=(LengthInRange(min_value=1), )),
    ),
    parameter_form=_parameter_valuespec_sophosxg_lic,
)

#!/usr/bin/env python3
"""Ruleset definition for SophosXG service check"""

# (c) Matthias Binder 'hds@kpc.de' - K&P Computer Service- und Vertriebs-GmbH
# (c) Andreas Doehler 'andreas.doehler@bechtle.com'
# License: GNU General Public License v2

from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    SingleChoice,
    SingleChoiceElement,
    String,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    HostAndItemCondition,
    LengthInRange,
    Topic,
)


def _parameter_valuespec_sophosxg_srv():
    return Dictionary(
        elements={
            "state": DictElement(
                parameter_form=SingleChoice(
                    title=Title("Wanted Service State"),
                    elements=[
                        SingleChoiceElement(
                            name="untouched",
                            title=Title("Untouched"),
                        ),
                        SingleChoiceElement(
                            name="stopped",
                            title=Title("Stopped"),
                        ),
                        SingleChoiceElement(
                            name="initializing",
                            title=Title("Initializing"),
                        ),
                        SingleChoiceElement(
                            name="running",
                            title=Title("Running"),
                        ),
                        SingleChoiceElement(
                            name="exiting",
                            title=Title("Exiting"),
                        ),
                        SingleChoiceElement(
                            name="dead",
                            title=Title("Dead"),
                        ),
                        SingleChoiceElement(
                            name="frozen",
                            title=Title("Frozen"),
                        ),
                        SingleChoiceElement(
                            name="unregistered",
                            title=Title("Unregistered"),
                        ),
                        SingleChoiceElement(
                            name="ignored",
                            title=Title("No preference / ignore state"),
                        ),
                    ],
                    prefill=DefaultValue("running"),
                ),
            ),
        }
    )


rule_spec_sophosxg_srv = CheckParameters(
    name="sophosxg_srv",
    title=Title("Sophos XG Services"),
    topic=Topic.NETWORKING,
    condition=HostAndItemCondition(
        item_title=Title("Service"),
        item_form=String(custom_validate=(LengthInRange(min_value=1),)),
    ),
    parameter_form=_parameter_valuespec_sophosxg_srv,
)

#!/usr/bin/env python3
"""Dell ME4 datasource program settings"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2


from cmk.rulesets.v1 import Title, Label
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DictElement,
    Dictionary,
    String,
    Password,
    validators,
    migrate_to_password,
)
from cmk.rulesets.v1.rule_specs import Topic, SpecialAgent



def _valuespec_special_agents_dellpowervault():
    return Dictionary(
        elements={
            "user": DictElement(
                parameter_form=String(
                    title=Title("Username"),
                ),
                required=True,
            ),
            "password": DictElement(
                parameter_form=Password(
                    title=Title("Password"),
                    custom_validate=(validators.LengthInRange(min_value=1),),
                    migrate=migrate_to_password,
                ),
                required=True,
            ),
            "verify_cert": DictElement(
                parameter_form=BooleanChoice(
                    label=Label("SSL certificate verification"),
                ),
                required=True,
            ),
        },
    )


rule_spec_dellpowervault = SpecialAgent(
    name="dellpowervault",
    title=Title("Dell Powervault M4 storage system"),
    topic=Topic.SERVER_HARDWARE,
    parameter_form=_valuespec_special_agents_dellpowervault,
)
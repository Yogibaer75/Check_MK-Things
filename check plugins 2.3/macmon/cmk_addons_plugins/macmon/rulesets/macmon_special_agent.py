#!/usr/bin/env python3
'''ruleset for macmon special agent'''
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Integer,
    String,
    Password,
    validators,
)
from cmk.rulesets.v1.rule_specs import Topic, SpecialAgent


def _valuespec_special_agents_macmon():
    return Dictionary(
        elements={
            "username": DictElement(
                parameter_form=String(
                    title=Title("Username"),
                    help_text=Help("User ID for web login"),
                ),
                required=True,
            ),
            "password": DictElement(
                parameter_form=Password(
                    title=Title("Password"),
                    help_text=Help("Password for the user"),
                    custom_validate=(validators.LengthInRange(min_value=1),),
                ),
                required=True,
            ),
            "port": DictElement(
                parameter_form=Integer(
                    title=Title("TCP Port"),
                    help_text=Help("Port number for API connection. Usually 8088"),
                    prefill=DefaultValue(443),
                    custom_validate=(
                        validators.NumberInRange(min_value=1, max_value=65535),
                    ),
                ),
                required=False,
            ),
        },
    )


rule_spec_macmon_datasource_programs = SpecialAgent(
    name="macmon",
    title=Title("Macmon"),
    topic=Topic.APPLICATIONS,
    parameter_form=_valuespec_special_agents_macmon,
)
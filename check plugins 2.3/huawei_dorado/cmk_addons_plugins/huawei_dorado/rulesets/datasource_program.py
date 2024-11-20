#!/usr/bin/env python3
"""parameter definition for special agent"""
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


def _valuespec_special_agent_huawei_dorado() -> Dictionary:
    return Dictionary(
        title=Title("Huawei Dorado Storage"),
        elements={
            "api_user": DictElement(
                parameter_form=String(
                    title=Title("Username"),
                ),
                required=True,
            ),
            "api_password": DictElement(
                parameter_form=Password(
                    title=Title("Password"),
                    custom_validate=(validators.LengthInRange(min_value=1),),
                ),
                required=True,
            ),
            "api_port": DictElement(
                parameter_form=Integer(
                    title=Title("TCP Port"),
                    help_text=Help("Port number for API connection. Usually 8088"),
                    prefill=DefaultValue(8088),
                    custom_validate=(
                        validators.NumberInRange(min_value=1, max_value=65535),
                    ),
                ),
                required=True,
            ),
        },
    )


rule_spec_huawei_dorado_datasource_programs = SpecialAgent(
    name="huawei_dorado",
    title=Title("Huawei Dorado Storage Controller"),
    topic=Topic.SERVER_HARDWARE,
    parameter_form=_valuespec_special_agent_huawei_dorado,
    help_text=(
        "This rule selects the Huawei Dorado special agent instead of normal CheckMK Agent"
    ),
)

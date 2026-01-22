#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rule set for checking ECI NPT devices using the special NPT SNMP agent."""
from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Integer,
    validators,
)
from cmk.rulesets.v1.rule_specs import Topic, SpecialAgent


def _valuespec_special_agents_npt_special() -> Dictionary:
    return Dictionary(
        title=Title("Check Interfaces of ECI NPT"),
        elements={
            "timeout": DictElement(
                parameter_form=Integer(
                    title=Title("Connection timeout"),
                    help_text=Help(
                        "The network timeout in seconds when communicating via SNMP."
                        "The default is 10 seconds. Please note that this "
                        "is not a total timeout, instead it is applied to each API call."
                    ),
                    prefill=DefaultValue(10),
                    custom_validate=(
                        validators.NumberInRange(min_value=1, max_value=30),
                    ),
                ),
            ),
        },
    )


rule_spec_npt_special = SpecialAgent(
    name="npt_special",
    title=Title("Check Interfaces of ECI NPT"),
    topic=Topic.NETWORKING,
    parameter_form=_valuespec_special_agents_npt_special,
    help_text=Help(
        "This rule selects the NPT agent, which uses Special NPT SNMP to gather information "
        "performance "
    ),
)

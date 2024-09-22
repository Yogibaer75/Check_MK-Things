#!/usr/bin/env python3
"""Windows dedup status bakery ruleset"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from cmk.rulesets.v1 import Title, Label, Help
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DictElement,
    Dictionary,
)
from cmk.rulesets.v1.rule_specs import AgentConfig, Topic


def _valuespec_agent_config_windows_dedup():
    return Dictionary(
        title=Title("Windows Dedup Status (Windows)"),
        help_text=Help(
            "This will deploy the agent plugin <tt>windows_dedup.ps1</tt> to check the Windows deduplication status."
        ),
        elements={
            "deploy": DictElement(
                parameter_form=BooleanChoice(
                    label=Label("Deploy Windows deduplication status plugin"),
                ),
                required=True,
            ),
        },
    )


rule_spec_agent_config_windows_patch_day = AgentConfig(
    title=Title("Windows Dedup Status"),
    topic=Topic.WINDOWS,
    name="windows_dedup",
    parameter_form=_valuespec_agent_config_windows_dedup,
)

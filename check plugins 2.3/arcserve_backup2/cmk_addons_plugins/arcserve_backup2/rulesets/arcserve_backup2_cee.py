#!/usr/bin/env python3
"""Arcserve backup 2 bakery ruleset"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from cmk.rulesets.v1 import Help, Label, Title
from cmk.rulesets.v1.form_specs import BooleanChoice, DictElement, Dictionary
from cmk.rulesets.v1.rule_specs import AgentConfig, Topic


def _valuespec_agent_config_arcserve_backup2():
    return Dictionary(
        title=Title("Arcserve Backup2 (Windows)"),
        help_text=Help(
            "This will deploy the agent plugin <tt>arcserve_backup2.ps1</tt> to check the Classic Arcserve status."
        ),
        elements={
            "deploy": DictElement(
                parameter_form=BooleanChoice(
                    label=Label("Deploy Arcserve backup status plugin"),
                ),
                required=True,
            ),
        },
    )


rule_spec_agent_config_windows_patch_day = AgentConfig(
    title=Title("Arcserve Backup2 Status"),
    topic=Topic.WINDOWS,
    name="arcserve_backup2",
    parameter_form=_valuespec_agent_config_arcserve_backup2,
)

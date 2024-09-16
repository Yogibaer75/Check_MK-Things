#!/usr/bin/env python3
"""Windows last update bakery ruleset"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from cmk.rulesets.v1 import Title, Label, Help
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DefaultValue,
    DictElement,
    Dictionary,
    Integer,
    MatchingScope,
    RegularExpression,
    List,
)
from cmk.rulesets.v1.rule_specs import AgentConfig, Topic


def _valuespec_agent_config_windows_patch_day():
    return Dictionary(
        title=Title("Windows Patch Day (Windows)"),
        help_text=Help(
            "This will deploy the agent plugin <tt>windows_patch_day.ps1</tt> to check the Windows update installation time."
            "As option you can set the maximum amount of updates in history that should be transfered. It is also possible to"
            "filter unwanted update entries like the daily Windows Defender Pattern updates."
        ),
        elements={
            "deploy": DictElement(
                parameter_form=BooleanChoice(
                    label=Label("Deploy Windows Patch day plugin"),
                ),
                required=True,
            ),
            "updatecount": DictElement(
                parameter_form=Integer(
                    title=Title("Update history count"),
                    prefill=DefaultValue(40),
                )
            ),
            "filterstring": DictElement(
                parameter_form=List(
                    title=Title("Unwanted updates (Regular Expressions)"),
                    help_text=Help(
                        "Regular expressions matching the begining of the installed update name."
                    ),
                    element_template=RegularExpression(
                        title=Title("Pattern"),
                        predefined_help_text=MatchingScope.INFIX,
                    ),
                    add_element_label=Label("Add new pattern"),
                ),
            ),
        },
    )


rule_spec_agent_config_windows_patch_day = AgentConfig(
    title=Title("Windows Patch Day"),
    topic=Topic.WINDOWS,
    name="windows_patch_day",
    parameter_form=_valuespec_agent_config_windows_patch_day,
)

#!/usr/bin/env python3
"""Ruleset definition for Windows firewall status check"""

# (c) Andreas Doehler 'andreas.doehler@bechtle.com'
# License: GNU General Public License v2

from cmk.rulesets.v1 import Help, Label, Title
from cmk.rulesets.v1.form_specs import (
    DictElement,
    Dictionary,
    List,
    SingleChoice,
    SingleChoiceElement,
    String,
    validators,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostCondition, Topic


def _parameter_valuespec_win_firewall_status():
    return Dictionary(
        elements={
            "profiles": DictElement(
                parameter_form=List(
                    title=Title("Firewall Profile configuration"),
                    help_text=Help("Please select the appropriate profile configuration."),
                    add_element_label=Label("Add profile"),
                    remove_element_label=Label("Remove profile"),
                    no_element_label=Label("No profile selected"),
                    element_template=Dictionary(
                        elements={
                            "profile": DictElement(
                                parameter_form=String(
                                    title=Title("Profile name"),
                                    custom_validate=(
                                        validators.LengthInRange(min_value=1),
                                    ),
                                    help_text=Help("Name of the firewall profile."),
                                ),
                            ),
                            "state": DictElement(
                                parameter_form=SingleChoice(
                                    title=Title("State"),
                                    help_text=Help("Profile state enabled or disabled"),
                                    elements=[
                                        SingleChoiceElement(
                                            name="Enabled",
                                            title=Title("Enabled"),
                                        ),
                                        SingleChoiceElement(
                                            name="Disabled",
                                            title=Title("Disabled"),
                                        ),
                                    ],
                                ),
                            ),
                            "incomming_action": DictElement(
                                parameter_form=SingleChoice(
                                    title=Title("Incomming Action"),
                                    help_text=Help(
                                        "Default behaviour for incomming traffic."
                                    ),
                                    elements=[
                                        SingleChoiceElement(
                                            name="Block",
                                            title=Title("Block"),
                                        ),
                                        SingleChoiceElement(
                                            name="Allow",
                                            title=Title("Allow"),
                                        ),
                                    ],
                                ),
                            ),
                            "outgoing_action": DictElement(
                                parameter_form=SingleChoice(
                                    title=Title("Outgoing Action"),
                                    help_text=Help(
                                        "Default behaviour for outgoing traffic."
                                    ),
                                    elements=[
                                        SingleChoiceElement(
                                            name="Block",
                                            title=Title("Block"),
                                        ),
                                        SingleChoiceElement(
                                            name="Allow",
                                            title=Title("Allow"),
                                        ),
                                    ],
                                ),
                            ),
                        },
                    ),
                ),
            ),
        }
    )


rule_spec_win_firewall_status = CheckParameters(
    name="win_firewall_status",
    title=Title("Windows Firewall Status"),
    topic=Topic.OPERATING_SYSTEM,
    condition=HostCondition(),
    parameter_form=_parameter_valuespec_win_firewall_status,
)

#!/usr/bin/env python3
"""Ruleset definition for HPE 3Par SSH agent"""

# (c) Andreas Doehler 'andreas.doehler@bechtle.com'
# License: GNU General Public License v2

from cmk.rulesets.v1 import Title, Help, Label
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DefaultValue,
    DictElement,
    Dictionary,
    MultipleChoice,
    MultipleChoiceElement,
    String,
)
from cmk.rulesets.v1.rule_specs import Topic, SpecialAgent


def _valuespec_special_agents_3par_ssh():
    return Dictionary(
        title=Title("HPE 3par with SSH"),
        elements={
            "user": DictElement(
                parameter_form=String(
                    title=Title("Username"),
                    help_text=Help("User name on the storage system. "
                                   "Read only permissions are sufficient."),
                ),
                required=True,
            ),
            "accept_any_hostkey": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("Accept any SSH Host Key"),
                    help_text=Help(
                        "Accepts any SSH Host Key presented by the storage device. "
                        "Please note: This might be a security issue because man-in-the-middle "
                        "attacks are not recognized! Better solution would be to add the "
                        "SSH Host Key of the monitored storage devices to the .ssh/known_hosts "
                        "file for the user your monitoring is running under (on OMD: the site user)"
                    ),
                    label=Label("Accept any SSH Host Key"),
                )
            ),
            "infos": DictElement(
                parameter_form=MultipleChoice(
                    title=Title("Retrieve information about..."),
                    elements=[
                        MultipleChoiceElement(
                            name="showcage", title=Title("Hosts Connected"),
                        ),
                        MultipleChoiceElement(
                            name="showpd", title=Title("Licensing Status"),
                        ),
                        MultipleChoiceElement(
                            name="showld", title=Title("MDisks"),
                        ),
                        MultipleChoiceElement(
                            name="showvv", title=Title("MDisksGrps"),
                        ),
                        MultipleChoiceElement(
                            name="showps", title=Title("IO Groups"),
                        ),
                        MultipleChoiceElement(
                            name="shownode", title=Title("Node Stats"),
                        ),
                    ],
                    prefill=DefaultValue(
                        [
                            "showcage",
                            "showpd",
                            "showld",
                            "showvv",
                            "showps",
                            "shownode",
                        ]
                    ),
                    show_toggle_all=True,
                ),
            ),
        },
    )


rule_spec_threepar_ssh_datasource_programs = SpecialAgent(
    name="threepar_ssh",
    title=Title("HPE 3par with SSH"),
    topic=Topic.STORAGE,
    parameter_form=_valuespec_special_agents_3par_ssh,
    help_text=(
        "This rule set selects the <tt>3par</tt> agent instead of the normal Check_MK Agent "
        "and allows monitoring of HPE 3par storage systems by calling "
        "show* commands there over SSH. "
        "Make sure you have SSH key authentication enabled for your monitoring user. "
        "That means: The user your monitoring is running under on the monitoring "
        "system must be able to ssh to the storage system as the user you gave below "
        "without password."
    ),
)

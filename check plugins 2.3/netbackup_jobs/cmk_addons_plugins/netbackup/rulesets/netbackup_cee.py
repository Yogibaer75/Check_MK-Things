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
    String,
)
from cmk.rulesets.v1.rule_specs import AgentConfig, Topic


def _valuespec_agent_config_netbackup():
    return Dictionary(
        title=Title("Netbackup Jobs (Windows)"),
        help_text=Help(
            "This will deploy the agent plugin <tt>netbackup_jobs.ps1</tt> to check the job status from Netbackup."
            "As option you can set the path to the Netbackup admincmd directory where the bperrror command is located."
        ),
        elements={
            "deploy": DictElement(
                parameter_form=BooleanChoice(
                    label=Label("Deploy Netbackup plugin"),
                ),
                required=True,
            ),
            "errorpath": DictElement(
                parameter_form=String(
                    title=Title("Path to Netbackup admincmd directory"),
                    prefill=DefaultValue(
                        "C:\\\\Program Files\\\\Veritas\\\\NetBackup\\\\bin\\\\admincmd\\\\"
                    ),
                    help_text=Help(
                        "Full path to the Netbackup admincmd directory where the bperror command is located."
                        "Path must end with a backslash (\\\\). All backslashes must be escaped twice(\\\\)."
                    ),
                )
            ),
        },
    )


rule_spec_agent_config_netbackup = AgentConfig(
    title=Title("Netbackup Jobs"),
    topic=Topic.WINDOWS,
    name="netbackup",
    parameter_form=_valuespec_agent_config_netbackup,
)

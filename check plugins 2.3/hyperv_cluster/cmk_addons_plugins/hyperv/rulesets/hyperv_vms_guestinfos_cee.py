#!/usr/bin/python
'''Deployment rule for Hyper-V VMs GuestInfos plugin'''
# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.rulesets.v1 import Help, Label, Title  # type: ignore[import]
from cmk.rulesets.v1.form_specs import (  # type: ignore[import]
    BooleanChoice,
    DictElement,
    Dictionary,
)
from cmk.rulesets.v1.rule_specs import AgentConfig, Topic  # type: ignore[import]


def _valuespec_agent_config_hyperv_hyperv_vm_info():
    return Dictionary(
        title=Title("Hyper-V VMs GuestInfos"),
        help_text=Help(
            "This plugin checks the status of Hyper-V VMs guestinfos."
        ),
        elements={
            "deploy": DictElement(
                parameter_form=BooleanChoice(
                    label=Label("Deploy plugin for Hyper-V VMs guestinfos"),
                ),
                required=True,
            ),
        },
    )


rule_spec_agent_config_hyperv_hyperv_vm_info = AgentConfig(
    title=Title("Hyper-V VMs GuestInfos"),
    topic=Topic.WINDOWS,
    name="hyperv_vm_info",
    parameter_form=_valuespec_agent_config_hyperv_hyperv_vm_info,
)

#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.rulesets.v1 import Title, Label, Help
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DictElement,
    Dictionary,
)
from cmk.rulesets.v1.rule_specs import AgentConfig, Topic


def _valuespec_agent_config_arcserve_udp():
    return Dictionary(
        title=Title("Arcserve UDP backup status (Windows)"),
        help_text=Help(
            "This rule deploys the agent plugin <tt>arcserve_udp.ps1</tt> to check the backup and "
            "Restore point status of the Arcserve Backup Server."
        ),
        elements={
            "deploy": DictElement(
                parameter_form=BooleanChoice(
                    label=Label("Deploy Arcserve UDP backup status"),
                ),
                required=True,
            ),
        },
    )


rule_spec_agent_config_windows_patch_day = AgentConfig(
    title=Title("Arcserve UDP backup status (Windows)"),
    topic=Topic.WINDOWS,
    name="arcserve_udp",
    parameter_form=_valuespec_agent_config_arcserve_udp,
)
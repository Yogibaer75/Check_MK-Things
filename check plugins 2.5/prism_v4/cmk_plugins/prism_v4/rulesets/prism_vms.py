#!/usr/bin/env python3
# Copyright (C) 2023 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.rulesets.v1 import Help, Title, form_specs, rule_specs

# value -> title, the values are the lower case power states reported by Nutanix
_VM_STATES = {
    "on": Title("On"),
    "unknown": Title("Unknown"),
    "off": Title("Off"),
    "powering_on": Title("Powering on"),
    "shutting_down": Title("Shutting down"),
    "powering_off": Title("Powered Off"),
    "pausing": Title("Pausing"),
    "paused": Title("Paused"),
    "suspending": Title("Suspending"),
    "suspended": Title("Suspended"),
    "resuming": Title("Resuming"),
    "resetting": Title("Resetting"),
    "migrating": Title("Migrating"),
}


def _parameter_form_prism_vms() -> form_specs.Dictionary:
    return form_specs.Dictionary(
        elements={
            "system_state": form_specs.DictElement(
                parameter_form=form_specs.SingleChoice(
                    title=Title("Wanted VM State"),
                    help_text=Help(
                        "The service is OK if the VM is in this state. Choose "
                        "'Ignore' to keep the service OK regardless of the VM state."
                    ),
                    elements=[
                        *(
                            form_specs.SingleChoiceElement(name=name, title=title)
                            for name, title in _VM_STATES.items()
                        ),
                        form_specs.SingleChoiceElement(name="ignore", title=Title("Ignore")),
                    ],
                    prefill=form_specs.DefaultValue("on"),
                ),
            ),
        },
        title=Title("Wanted VM State for defined Nutanix VMs"),
    )


rule_spec_prism_vms = rule_specs.CheckParameters(
    name="prism_vms",
    topic=rule_specs.Topic.VIRTUALIZATION,
    parameter_form=_parameter_form_prism_vms,
    title=Title("Nutanix VM State"),
    condition=rule_specs.HostAndItemCondition(item_title=Title("VM")),
)

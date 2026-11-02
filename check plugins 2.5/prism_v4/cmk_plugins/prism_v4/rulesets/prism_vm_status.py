#!/usr/bin/env python3
# Copyright (C) 2023 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.plugins.prism_v4.lib_v4 import PRISM_POWER_STATES
from cmk.rulesets.v1 import Help, Title, form_specs, rule_specs

_STATUS_CHOICE: dict[str, Title] = {
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
    "undetermined": Title("Undetermined"),
}


def _parameters_valuespec_prism_vms() -> form_specs.Dictionary:
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
                            for name, title in _STATUS_CHOICE.items()
                        ),
                        form_specs.SingleChoiceElement(name="ignore", title=Title("Ignore")),
                    ],
                    prefill=form_specs.DefaultValue("on"),
                ),
            ),
            "power_states": form_specs.DictElement(
                parameter_form=form_specs.Dictionary(
                    title=Title("State mapping for power states"),
                    help_text=Help(
                        "Monitoring state of the service if the VM is not in the wanted "
                        "state. Power states which are not configured here keep their "
                        "default mapping."
                    ),
                    elements={
                        name: form_specs.DictElement(
                            parameter_form=form_specs.ServiceState(
                                title=title,
                                prefill=form_specs.DefaultValue(PRISM_POWER_STATES.get(name, 3)),
                            ),
                        )
                        for name, title in _STATUS_CHOICE.items()
                    },
                ),
            ),
            "other_power_state": form_specs.DictElement(
                parameter_form=form_specs.ServiceState(
                    title=Title("State for unknown power states"),
                    help_text=Help(
                        "Used for power states reported by Nutanix which are not part of "
                        "the mapping above."
                    ),
                    prefill=form_specs.DefaultValue(form_specs.ServiceState.UNKNOWN),
                ),
            ),
        },
        title=Title("Wanted VM State for defined Nutanix VMs"),
    )


rule_spec_prism_vm_status = rule_specs.CheckParameters(
    name="prism_vm_status",
    topic=rule_specs.Topic.VIRTUALIZATION,
    parameter_form=_parameters_valuespec_prism_vms,
    title=Title("Nutanix single VM State"),
    condition=rule_specs.HostCondition(),
)
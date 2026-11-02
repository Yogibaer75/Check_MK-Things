#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.rulesets.v1 import Help, Label, Title, form_specs, rule_specs


def _parameter_form_prism_vm_categories() -> form_specs.Dictionary:
    return form_specs.Dictionary(
        elements={
            "expected": form_specs.DictElement(
                parameter_form=form_specs.List(
                    title=Title("Expected categories"),
                    help_text=Help(
                        "Categories which have to be assigned to the VM. Leave the value "
                        "empty to accept any value of the category."
                    ),
                    element_template=form_specs.Dictionary(
                        elements={
                            "key": form_specs.DictElement(
                                parameter_form=form_specs.String(
                                    title=Title("Category name"),
                                    custom_validate=(
                                        form_specs.validators.LengthInRange(min_value=1),
                                    ),
                                ),
                                required=True,
                            ),
                            "value": form_specs.DictElement(
                                parameter_form=form_specs.String(
                                    title=Title("Category value"),
                                ),
                            ),
                        },
                    ),
                    add_element_label=Label("Add category"),
                ),
            ),
            "state_missing": form_specs.DictElement(
                parameter_form=form_specs.ServiceState(
                    title=Title("State if an expected category is missing"),
                    prefill=form_specs.DefaultValue(form_specs.ServiceState.WARN),
                ),
            ),
            "state_unexpected": form_specs.DictElement(
                parameter_form=form_specs.ServiceState(
                    title=Title("State if a category is assigned which is not expected"),
                    help_text=Help("Only evaluated if expected categories are configured."),
                    prefill=form_specs.DefaultValue(form_specs.ServiceState.OK),
                ),
            ),
        },
        title=Title("Expected categories of Nutanix VMs"),
    )


rule_spec_prism_vm_categories = rule_specs.CheckParameters(
    name="prism_vm_categories",
    topic=rule_specs.Topic.VIRTUALIZATION,
    parameter_form=_parameter_form_prism_vm_categories,
    title=Title("Nutanix VM Categories"),
    condition=rule_specs.HostCondition(),
)

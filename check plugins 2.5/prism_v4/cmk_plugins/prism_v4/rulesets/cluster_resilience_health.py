#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.rulesets.v1 import Help, Title, form_specs, rule_specs


def _parameter_form_prism_cluster_resilience() -> form_specs.Dictionary:
    return form_specs.Dictionary(
        elements={
            "state_degraded": form_specs.DictElement(
                parameter_form=form_specs.ServiceState(
                    title=Title("State if the fault tolerance is too low"),
                    help_text=Help(
                        "Used if the current fault tolerance is below the desired fault "
                        "tolerance of the cluster or below the configured minimum."
                    ),
                    prefill=form_specs.DefaultValue(form_specs.ServiceState.CRIT),
                ),
            ),
            "min_fault_tolerance": form_specs.DictElement(
                parameter_form=form_specs.Integer(
                    title=Title("Minimum fault tolerance"),
                    help_text=Help(
                        "Number of failures the cluster has to survive. This is checked "
                        "independently of the desired fault tolerance configured in the "
                        "cluster, e.g. to alert on clusters configured without redundancy."
                    ),
                    prefill=form_specs.DefaultValue(1),
                    custom_validate=(form_specs.validators.NumberInRange(min_value=0),),
                ),
            ),
        },
        title=Title("Nutanix cluster resilience"),
    )


rule_spec_prism_cluster_resilience = rule_specs.CheckParameters(
    name="prism_cluster_resilience",
    topic=rule_specs.Topic.VIRTUALIZATION,
    parameter_form=_parameter_form_prism_cluster_resilience,
    title=Title("Nutanix Cluster Resilience"),
    condition=rule_specs.HostCondition(),
)


def _parameter_form_prism_cluster_health() -> form_specs.Dictionary:
    return form_specs.Dictionary(
        elements={
            "levels_lower": form_specs.DictElement(
                parameter_form=form_specs.SimpleLevels(
                    title=Title("Lower levels for the health score"),
                    help_text=Help("The health score of the cluster ranges from 0 to 100."),
                    form_spec_template=form_specs.Integer(),
                    level_direction=form_specs.LevelDirection.LOWER,
                    prefill_fixed_levels=form_specs.DefaultValue((70, 50)),
                ),
            ),
        },
        title=Title("Nutanix cluster health"),
    )


rule_spec_prism_cluster_health = rule_specs.CheckParameters(
    name="prism_cluster_health",
    topic=rule_specs.Topic.VIRTUALIZATION,
    parameter_form=_parameter_form_prism_cluster_health,
    title=Title("Nutanix Cluster Health"),
    condition=rule_specs.HostCondition(),
)

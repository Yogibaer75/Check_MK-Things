#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    InputHint,
    Integer,
    LevelDirection,
    migrate_to_integer_simple_levels,
    ServiceState,
    SimpleLevels,
    String,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    Topic,
    HostAndItemCondition,
    LengthInRange,
    Help,
)


def _parameter_valuespec_arcserve_udp_jobs():
    return Dictionary(
        elements={
            "levels": DictElement[Integer](
                parameter_form=SimpleLevels(
                    title=Title("Backup age"),
                    help_text=Help(
                        "The age of the last backup in hours. The value is calculated from the last backup time."
                    ),
                    migrate=migrate_to_integer_simple_levels,
                    form_spec_template=Integer(unit_symbol="hours"),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint((36, 72)),
                ),
            ),
            "no_backup": DictElement(
                parameter_form=ServiceState(
                    title=Title("Interpretation of no existing backup"),
                    prefill=DefaultValue(ServiceState.OK),
                ),
            ),
        },
    )


rule_spec_arcserve_udp_jobs = CheckParameters(
    name="arcserve_udp_jobs",
    title=Title("Arcserve UDP Jobs"),
    topic=Topic.APPLICATIONS,
    condition=HostAndItemCondition(
        item_title=Title("Servername"),
        item_form=String(custom_validate=(LengthInRange(min_value=1),)),
    ),
    parameter_form=_parameter_valuespec_arcserve_udp_jobs,
)


def _parameter_valuespec_arcserve_udp_backup():
    return Dictionary(
        elements={
            "levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("maximal amount of recovery points"),
                    help_text=Help(
                        "The maximum number of restore points that are available for the last backup."
                    ),
                    form_spec_template=Integer(unit_symbol="restore points"),
                    migrate=migrate_to_integer_simple_levels,
                    prefill_fixed_levels=InputHint((40, 60)),
                    level_direction=LevelDirection.UPPER,
                ),
            ),
            "levels_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("minimal amount of recovery points"),
                    help_text=Help(
                        "The minimum number of restore points that are available for the last backup."
                    ),
                    form_spec_template=Integer(unit_symbol="restore points"),
                    migrate=migrate_to_integer_simple_levels,
                    prefill_fixed_levels=InputHint((5, 1)),
                    level_direction=LevelDirection.LOWER,
                ),
            ),
            "no_backup": DictElement(
                parameter_form=ServiceState(
                    title=Title("Interpretation of no existing backup"),
                    prefill=DefaultValue(ServiceState.OK),
                ),
            ),
        },
    )


rule_spec_arcserve_udp_backup = CheckParameters(
    name="arcserve_udp_backup",
    title=Title("Arcserve UDP Backup"),
    topic=Topic.APPLICATIONS,
    condition=HostAndItemCondition(
        item_title=Title("Servername"),
        item_form=String(custom_validate=(LengthInRange(min_value=1),)),
    ),
    parameter_form=_parameter_valuespec_arcserve_udp_backup,
)

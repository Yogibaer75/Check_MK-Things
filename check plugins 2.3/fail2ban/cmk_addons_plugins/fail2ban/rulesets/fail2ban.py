#!/usr/bin/env python3

# (c) Jens Kühnel <fail2ban-checkmk@jens.kuehnel.org> 2021
# migrated to CMK 2.3 Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
#
# Information about fail2ban check_mk module see:
# https://github.com/JensKuehnel/fail2ban-check-mk
#
# License: GNU General Public License v2

from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import (
    DictElement,
    Dictionary,
    InputHint,
    Integer,
    LevelDirection,
    migrate_to_integer_simple_levels,
    SimpleLevels,
    String,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, Topic, HostAndItemCondition, LengthInRange


def _parameter_valuespec_fail2ban():
    return Dictionary(
        elements={
            "banned": DictElement(
                parameter_form=SimpleLevels[int](
                    title=Title("Number of banned IPs"),
                    help_text=Help("This number of IPs have failed multiple times and "
                                   "are banned of a configure amount of times."),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(),
                    migrate=migrate_to_integer_simple_levels,
                    prefill_fixed_levels=InputHint(value=(10, 20)),
                ),
            ),
            "failed": DictElement(
                parameter_form=SimpleLevels[int](
                    title=Title("Number of failed IPs"),
                    help_text=Help("This number of IPs have failed logins. "
                                   "If this happens multiple times they will be banned."),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(),
                    migrate=migrate_to_integer_simple_levels,
                    prefill_fixed_levels=InputHint(value=(30, 40)),
                ),
            ),
        }
    )


rule_spec_fail2ban = CheckParameters(
    name="fail2ban",
    title=Title("Number of fail2ban Banned/Failed IPs"),
    topic=Topic.NETWORKING,
    condition=HostAndItemCondition(
        item_title=Title("Jail name"),
        item_form=String(custom_validate=(LengthInRange(min_value=1),)),
    ),
    parameter_form=_parameter_valuespec_fail2ban,
)

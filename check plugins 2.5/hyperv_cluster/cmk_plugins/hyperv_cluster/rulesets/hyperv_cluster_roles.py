#!/usr/bin/python

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from collections.abc import Mapping

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    SingleChoice,
    SingleChoiceElement,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic


def _migrate(value: object) -> Mapping[str, object]:
    """Read the parameters of the Hyper-V MKP from the Checkmk Exchange

    The MKP had a default state plus a list of per-VM states. Only the default
    state is kept, per-VM states are set with the item condition of a rule.

    >>> _migrate({"default_status": "inactive", "match_services": []})
    {'expected_state': 'inactive'}
    """
    match value:
        case {"expected_state": str(expected_state)}:
            return {"expected_state": expected_state}
        case dict():
            return {"expected_state": value.get("default_status", "active")}
    raise TypeError(value)


def _parameter_form_hyperv_cluster_roles() -> Dictionary:
    return Dictionary(
        elements={
            "expected_state": DictElement(
                required=True,
                parameter_form=SingleChoice(
                    title=Title("Expected power state"),
                    help_text=Help(
                        "If the VM is not in the expected power state, for example partially "
                        "online or pending, the service is WARN. A failed VM is always CRIT, "
                        "also if the power state is ignored."
                    ),
                    elements=[
                        SingleChoiceElement(name="active", title=Title("Online")),
                        SingleChoiceElement(name="inactive", title=Title("Offline")),
                        SingleChoiceElement(name="ignore", title=Title("Ignore the power state")),
                    ],
                    prefill=DefaultValue("active"),
                ),
            ),
        },
        migrate=_migrate,
    )


rule_spec_hyperv_cluster_roles = CheckParameters(
    name="hyperv_cluster_roles",
    title=Title("Hyper-V cluster VM state"),
    topic=Topic.VIRTUALIZATION,
    condition=HostAndItemCondition(item_title=Title("VM name")),
    parameter_form=_parameter_form_hyperv_cluster_roles,
)

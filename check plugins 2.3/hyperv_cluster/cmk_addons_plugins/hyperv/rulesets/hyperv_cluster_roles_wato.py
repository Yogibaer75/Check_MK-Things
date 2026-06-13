#!/usr/bin/python

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.rulesets.v1 import Title  # type: ignore[import]
from cmk.rulesets.v1.form_specs import (  # type: ignore[import]
    DefaultValue,
    DictElement,
    Dictionary,
    List,
    SingleChoice,
    SingleChoiceElement,
    String,
)
from cmk.rulesets.v1.rule_specs import (  # type: ignore[import]
    CheckParameters,
    HostAndItemCondition,
    LengthInRange,
    Topic,
)


def _migrate_tuple(value) -> list[dict[str, str]]:
    """
    Convert a list of tuple to a list of dictionary with keys 'service_name' and 'state'.
    """
    if isinstance(value, list):
        if all(isinstance(item, dict) for item in value):
            return value
        ITEMLENGTH = 2
        return [
            {
                "service_name": item[0],
                "state": item[1],
            }
            for item in value
            if isinstance(item, tuple) and len(item) == ITEMLENGTH
        ]
    return value


def _parameter_valuespec_hyperv_cluster_roles():
    return Dictionary(
        elements={
            "default_status": DictElement(
                parameter_form=SingleChoice(
                    title=Title("Default State"),
                    elements=[
                        SingleChoiceElement(
                            name="active",
                            title=Title("active"),
                        ),
                        SingleChoiceElement(
                            name="inactive",
                            title=Title("inactive"),
                        ),
                        SingleChoiceElement(
                            name="ignore",
                            title=Title("ignore"),
                        ),
                    ],
                    prefill=DefaultValue("active"),
                ),
            ),
            "match_services": DictElement(
                parameter_form=List(
                    title=Title("Special States"),
                    migrate=_migrate_tuple,
                    element_template=Dictionary(
                        elements={
                            "service_name": DictElement(
                                required=True,
                                parameter_form=String(
                                    title=Title("Service name"),
                                    custom_validate=(LengthInRange(min_value=1),),
                                ),
                            ),
                            "state": DictElement(
                                required=True,
                                parameter_form=SingleChoice(
                                    title=Title("State"),
                                    elements=[
                                        SingleChoiceElement(
                                            name="active",
                                            title=Title("active"),
                                        ),
                                        SingleChoiceElement(
                                            name="inactive",
                                            title=Title("inactive"),
                                        ),
                                        SingleChoiceElement(
                                            name="ignore",
                                            title=Title("ignore"),
                                        ),
                                    ],
                                ),
                            ),
                        }
                    ),
                ),
            ),
        }
    )


rule_spec_hyperv_cluster_roles = CheckParameters(
    name="hyperv_cluster_roles",
    title=Title("Hyper-V Cluster Role Status"),
    topic=Topic.APPLICATIONS,
    condition=HostAndItemCondition(
        item_title=Title("Cluster Role"),
        item_form=String(custom_validate=(LengthInRange(min_value=1),)),
    ),
    parameter_form=_parameter_valuespec_hyperv_cluster_roles,
)

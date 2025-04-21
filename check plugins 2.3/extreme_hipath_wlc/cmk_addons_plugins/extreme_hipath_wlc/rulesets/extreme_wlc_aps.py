#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    SingleChoice,
    SingleChoiceElement,
    String,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    HostAndItemCondition,
    LengthInRange,
    Topic,
)


def _parameter_valuespec_extreme_wlc_aps():
    return Dictionary(
        elements={
            "state": DictElement(
                parameter_form=SingleChoice(
                    title=Title("Device state"),
                    elements=[
                        SingleChoiceElement(
                            name="state_1",
                            title=Title("Up"),
                        ),
                        SingleChoiceElement(
                            name="state_2",
                            title=Title("Down"),
                        ),
                        SingleChoiceElement(
                            name="state_3",
                            title=Title("Ignore"),
                        ),
                    ],
                    prefill=DefaultValue("state_1"),
                ),
            ),
            "location": DictElement(
                parameter_form=SingleChoice(
                    title=Title("Device location"),
                    elements=[
                        SingleChoiceElement(
                            name="local",
                            title=Title("Registered on local WLC"),
                        ),
                        SingleChoiceElement(
                            name="foreign",
                            title=Title("Registered on foreign WLC"),
                        ),
                        SingleChoiceElement(
                            name="both",
                            title=Title("Ignore the registered WLC"),
                        ),
                    ],
                    prefill=DefaultValue("local"),
                ),
            ),
        },
    )


rule_spec_extreme_wlc_aps = CheckParameters(
    name="extreme_wlc_aps",
    title=Title("AP Status"),
    topic=Topic.NETWORKING,
    condition=HostAndItemCondition(
        item_title=Title("AP name"),
        item_form=String(custom_validate=(LengthInRange(min_value=1),)),
    ),
    parameter_form=_parameter_valuespec_extreme_wlc_aps,
)

#!/usr/bin/env python3
"""Oracle ILOM sensor parameters"""
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersEnvironment,
)
from cmk.gui.valuespec import Dictionary, DropdownChoice, Float, TextInput, Tuple


def _parameter_valuespec_ilom_sensor() -> Dictionary:
    return Dictionary(
        elements=[
            (
                "levels",
                Tuple(
                    title=_("Upper Sensor Levels"),
                    elements=[
                        Float(title=_("Warning at")),
                        Float(title=_("Critical at")),
                    ],
                ),
            ),
            (
                "levels_lower",
                Tuple(
                    title=_("Lower Sensor Levels"),
                    elements=[
                        Float(title=_("Warning below")),
                        Float(title=_("Critical below")),
                    ],
                ),
            ),
            (
                "device_levels_handling",
                DropdownChoice(
                    title=_("Interpretation of the device's own temperature status"),
                    choices=[
                        ("usr", _("Ignore device's own levels")),
                        ("dev", _("Only use device's levels, ignore yours")),
                        (
                            "devdefault",
                            _("Use device's levels if present, otherwise yours"),
                        ),
                        (
                            "usrdefault",
                            _("Use your own levels if present, otherwise the device's"),
                        ),
                    ],
                    default_value="usrdefault",
                ),
            ),
        ],
        ignored_keys=["_item_key"],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="ilom_sensor",
        group=RulespecGroupCheckParametersEnvironment,
        item_spec=lambda: TextInput(
            title=_("Sensor ID"), help=_("The identifier of the sensor.")
        ),
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_ilom_sensor,
        title=lambda: _("Oracle ILOM Sensor"),
    )
)

#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
"""parameters for BACS battery check"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    Float,
    TextAscii,
    Tuple,
)

from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersEnvironment,
)


def _parameter_valuespec_bacs_battery():
    return Dictionary(
        title=_("Voltage Sensor"),
        optional_keys=True,
        elements=[
            (
                "voltage",
                Tuple(
                    title=_("Upper Levels for Voltage"),
                    elements=[
                        Float(title=_("Warning over"), default_value=14.00, unit="V"),
                        Float(title=_("Critical over"), default_value=15.00, unit="V"),
                    ],
                ),
            ),
            (
                "voltage_lower",
                Tuple(
                    title=_("Lower Levels for Voltage"),
                    elements=[
                        Float(title=_("Warning below"), default_value=10.00, unit="V"),
                        Float(title=_("Critical below"), default_value=9.00, unit="V"),
                    ],
                ),
            ),
            (
                "temp",
                Tuple(
                    title=_("Upper Levels for Temperature"),
                    elements=[
                        Float(title=_("Warning below"), default_value=40.00, unit="°C"),
                        Float(
                            title=_("Critical below"), default_value=50.00, unit="°C"
                        ),
                    ],
                ),
            ),
            (
                "temp_lower",
                Tuple(
                    title=_("Lower Levels for Temperature"),
                    elements=[
                        Float(title=_("Warning below"), default_value=10.00, unit="°C"),
                        Float(title=_("Critical below"), default_value=5.00, unit="°C"),
                    ],
                ),
            ),
            (
                "resistance",
                Tuple(
                    title=_("Levels for inside Resistance"),
                    elements=[
                        Float(title=_("Warning over"), default_value=15.00, unit="mOhm"),
                        Float(
                            title=_("Critical over"), default_value=18.00, unit="mOhm"
                        ),
                    ],
                ),
            ),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="bacs",
        group=RulespecGroupCheckParametersEnvironment,
        item_spec=lambda: TextAscii(
            title=_("Battery Index"),
        ),
        parameter_valuespec=_parameter_valuespec_bacs_battery,
        title=lambda: _("BACS Battery"),
    )
)

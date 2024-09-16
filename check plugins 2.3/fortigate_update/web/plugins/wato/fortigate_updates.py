#!/usr/bin/env python3
"""Ruleset definition for Fortigate update check"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersNetworking,
)
from cmk.gui.valuespec import Dictionary, Integer, Tuple, Checkbox, TextInput


def _parameter_valuespec_fortigate_update() -> Dictionary:
    return Dictionary(
        elements=[
            (
                "levels",
                Tuple(
                    title=_("Days since last update check"),
                    help=_("This rule sets the levels of the checked value."),
                    elements=[
                        Integer(title=_("Warning at"), default_value=30),
                        Integer(title=_("Critical at"), default_value=90),
                    ],
                ),
            ),
            (
                "no_levels",
                Checkbox(
                    title=_("Do not impose levels"),
                    label=_("no levels"),
                    default_value=False,
                ),
            ),
        ]
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="fortigate_update",
        item_spec=lambda: TextInput(title=_("Update Name")),
        group=RulespecGroupCheckParametersNetworking,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_fortigate_update,
        title=lambda: _("Fortigate Update"),
    )
)

#!/usr/bin/env python3
"""Ruleset definition for Windows firewall status check"""

# (c) Andreas Doehler 'andreas.doehler@bechtle.com'
# License: GNU General Public License v2

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    DropdownChoice,
    ListOf,
    Tuple,
    TextAscii,
)

from cmk.gui.plugins.wato.utils import (
    rulespec_registry,
    CheckParameterRulespecWithoutItem,
    RulespecGroupCheckParametersOperatingSystem,
)


def _parameter_valuespec_win_firewall_status():
    return Dictionary(
        title=_("Firewall Profile configuration"),
        elements=[
            (
                "profiles",
                ListOf(
                    Tuple(
                        elements=[
                            TextAscii(
                                title=_("Profile name"),
                                help=_("Name of the firewall profile."),
                            ),
                            DropdownChoice(
                                title=_("State"),
                                help=_("Profile state active or inaktive"),
                                choices=[
                                    ("True", _("Enabled")),
                                    ("False", _("Disabled")),
                                ],
                            ),
                            DropdownChoice(
                                title=_("Incomming Action"),
                                help=_("Default behaviour for incomming traffic."),
                                choices=[
                                    ("Block", _("Block")),
                                    ("Allow", _("Allow")),
                                ],
                            ),
                            DropdownChoice(
                                title=_("Outgoing Action"),
                                help=_("Default behaviour for outgoing traffic."),
                                choices=[
                                    ("Block", _("Block")),
                                    ("Allow", _("Allow")),
                                ],
                            ),
                        ],
                    ),
                    title=_("Firewall Profile configuration"),
                    help=_("Please select the abropriate profile configuration."),
                    allow_empty=False,
                    default_value=[
                        ("Domain", "True", "Block", "Allow"),
                        ("Private", "True", "Block", "Allow"),
                        ("Public", "True", "Block", "Allow"),
                    ],
                ),
            ),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="win_firewall_status",
        group=RulespecGroupCheckParametersOperatingSystem,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_win_firewall_status,
        title=lambda: _("Windows Firewall Status"),
    )
)

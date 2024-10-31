#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    HostRulespec,
    RulespecGroupCheckParametersDiscovery,
    rulespec_registry,
)
from cmk.gui.valuespec import Dictionary, DropdownChoice


def _valuespec_discovery_redfish_outlets():
    return Dictionary(
        title=_("Redfish outlet discovery"),
        help=_("Specify how to name the outlets at discovered"),
        elements=[
            (
                "naming",
                DropdownChoice(
                    title=_("Naming of outlets at discovery"),
                    default_value="index",
                    help=_("Specify how to name the outlets at discovered"),
                    choices=[
                        ("index", _("Port Index")),
                        ("label", _("User Label")),
                        ("fill", _("Port Index with fill")),
                    ],
                ),
            ),
        ],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupCheckParametersDiscovery,
        match_type="all",
        name="discovery_redfish_outlets",
        valuespec=_valuespec_discovery_redfish_outlets,
    )
)

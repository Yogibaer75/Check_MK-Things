#!/usr/bin/env python3
"""Ruleset definition for SophosXG version check"""

# (c) Matthias Binder 'hds@kpc.de' - K&P Computer Service- und Vertriebs-GmbH
# (c) Andreas Doehler 'andreas.doehler@bechtle.com'
# License: GNU General Public License v2

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    rulespec_registry,
    CheckParameterRulespecWithoutItem,
    RulespecGroupCheckParametersNetworking,
)
from cmk.gui.valuespec import (
    Dictionary,
    TextInput,
)


def _parameter_valuespec_sophosxg_version():
    return Dictionary(
        elements=[
            (
                "firmware_check",
                TextInput(
                    title=_("Expected Firmware version"),
                    default_value="0",
                ),
            ),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="snmp_sophosxg_version",
        group=RulespecGroupCheckParametersNetworking,
        parameter_valuespec=_parameter_valuespec_sophosxg_version,
        title=lambda: _("Sophos XG Firmware"),
    )
)

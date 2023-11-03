#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Matthias Binder 'hds@kpc.de'
# Rework: Andreas Doehler 'andreas.doehler@bechtle.com'
# License: GNU General Public License

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    rulespec_registry,
    CheckParameterRulespecWithItem,
    RulespecGroupCheckParametersNetworking,
)

from cmk.gui.valuespec import (
    Dictionary,
    TextInput,
    DropdownChoice,
)


def _parameter_valuespec_sophosxg_srv():
    status_choice = [
        ("0", _("Untouched")),
        ("1", _("Stopped")),
        ("2", _("Initializing")),
        ("3", _("Running")),
        ("4", _("Exiting")),
        ("5", _("Dead")),
        ("6", _("Frozen")),
        ("7", _("Unregistered")),
        ("99", _("No preference / ignore state")),
    ]
    return Dictionary(
        elements=[
            ("state", DropdownChoice(
                title=_("Wanted Service State"),
                choices=status_choice,
                default_value="3",
            )),
        ],
        title=_("Wanted Service State"),
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="sophosxg_srv",
        group=RulespecGroupCheckParametersNetworking,
        item_spec=lambda: TextInput(title=_("Service")),
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_sophosxg_srv,
        title=lambda: _("Sophos XG Services"),
    )
)

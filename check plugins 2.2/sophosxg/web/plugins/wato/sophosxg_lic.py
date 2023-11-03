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
    Tuple,
    Integer,
)


def _parameter_valuespec_sophosxg_lic():
    status_choice = [
        ("0", _("None")),
        ("1", _("Evaluating")),
        ("2", _("Not Subscribed")),
        ("3", _("Subscribed")),
        ("4", _("Expired")),
        ("5", _("Deactivated")),
        ("99", _("No preference selected / ignored")),
    ]
    return Dictionary(
        elements=[
            (
                "levels",
                Tuple(
                    title=_("License Days Levels"),
                    elements=[
                        Integer(
                            title=_("Warning when License expires \
                                     in under X days"),
                            default_value=40,
                        ),
                        Integer(
                            title=_("Critical when License expires \
                                     in under X days"),
                            default_value=30,
                        ),
                    ],
                ),
            ),
            (
                "state",
                DropdownChoice(
                    title=_("Wanted Licecense State"),
                    choices=status_choice,
                    default_value="3",
                ),
            ),
        ],
        title=_("Wanted License State and Runtime Levels"),
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="sophosxg_lic",
        group=RulespecGroupCheckParametersNetworking,
        item_spec=lambda: TextInput(title=_("License")),
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_sophosxg_lic,
        title=lambda: _("Sophos XG State for Licenses & Runtime"),
    )
)

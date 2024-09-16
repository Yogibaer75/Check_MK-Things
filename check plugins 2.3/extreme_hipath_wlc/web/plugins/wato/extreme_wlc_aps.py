#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    DropdownChoice,
    TextAscii,
    Transform,
)

from cmk.gui.plugins.wato.utils import (
    RulespecGroupCheckParametersNetworking,
    CheckParameterRulespecWithItem,
    rulespec_registry,
)


def _parameter_valuespec_extreme_wlc_aps():
    return Transform(
        Dictionary(
            elements=[
                (
                    "state",
                    DropdownChoice(
                        title=_("Device state"),
                        choices=[
                            (1, _("Up")),
                            (2, _("Down")),
                            (3, _("Ignore")),
                        ],
                        default_value=1,
                    ),
                ),
                (
                    "location",
                    DropdownChoice(
                        title=_("Device location"),
                        choices=[
                            ("local", _("Registered on local WLC")),
                            ("foreign", _("Registered on foreign WLC")),
                            ("both", _("Ignore the registered WLC")),
                        ],
                        default_value="local",
                    ),
                ),
            ],
        ),
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="extreme_wlc_aps",
        group=RulespecGroupCheckParametersNetworking,
        item_spec=lambda: TextAscii(
            title=_("AP name"), help=_("The identifier of the AP.")
        ),
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_extreme_wlc_aps,
        title=lambda: _("AP Status"),
    )
)

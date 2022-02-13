#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    DropdownChoice,
    Float,
    TextAscii,
    Transform,
    Tuple,
)
from cmk.gui.plugins.wato import (
    RulespecGroupCheckParametersEnvironment,
    CheckParameterRulespecWithItem,
    rulespec_registry,
)


def _parameter_valuespec_fanspeed():
    return Transform(
        Dictionary(elements=[
            (
                "levels",
                Transform(
                    Tuple(
                        title=_("Upper levels for the fan speed"),
                        elements=[
                            Float(title=_("Warning at"), unit=u"rpm", default_value=12000),
                            Float(title=_("Critical at"), unit=u"rpm", default_value=15000),
                        ],
                    ),
                    forth=lambda elems: (float(elems[0]), float(elems[1])),
                ),
            ),
            (
                "levels_lower",
                Transform(
                    Tuple(
                        title=_("Lower levels for the fan speed"),
                        elements=[
                            Float(title=_("Warning below"), unit=u"rpm", default_value=300),
                            Float(title=_("Critical below"), unit=u"rpm", default_value=100),
                        ],
                    ),
                    forth=lambda elems: (float(elems[0]), float(elems[1])),
                ),
            ),
            ("device_levels_handling",
             DropdownChoice(
                 title=_("Interpretation of the device's own fan speed status"),
                 choices=[
                     ("usr", _("Ignore device's own levels")),
                     ("dev", _("Only use device's levels, ignore yours")),
                     ("best", _("Use least critical of your and device's levels")),
                     ("worst", _("Use most critical of your and device's levels")),
                     ("devdefault", _("Use device's levels if present, otherwise yours")),
                     ("usrdefault", _("Use your own levels if present, otherwise the device's")),
                 ],
                 default_value="usrdefault",
             )),
        ],),
        forth=lambda v: isinstance(v, tuple) and {"levels": v} or v,
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="fanspeed",
        group=RulespecGroupCheckParametersEnvironment,
        item_spec=lambda: TextAscii(title=_("Fan ID"),
                                    help=_("The identifier of the fan sensor.")),
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_fanspeed,
        title=lambda: _("Fanspeed"),
    ))

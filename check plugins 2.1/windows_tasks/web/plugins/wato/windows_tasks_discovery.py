#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    ListOfStrings,
)

from cmk.gui.plugins.wato import (
    rulespec_registry,
    RulespecGroupCheckParametersDiscovery,
    HostRulespec,
)


def _valuespec_discovery_windows_tasks_rules():
    return Dictionary(
        title=_("Windows tasks states to ignore for discovery"),
        elements=[
            (
                "state",
                ListOfStrings(
                    title=_("ignored State"),
                    help=_("State name to ignore at discovery time."),
                    default_value=["Disabled", "Deaktiviert"],
                ),
            ),
        ],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupCheckParametersDiscovery,
        match_type="dict",
        name="discovery_windows_tasks_rules",
        valuespec=_valuespec_discovery_windows_tasks_rules,
    )
)
